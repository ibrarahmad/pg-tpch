#!/bin/bash

shopt -s nullglob

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)
. "$BASEDIR/conf/pgtpch_defaults"

start_cluster()
{
    echo "starting cluster ..."
    sudo -u $PGUSER $PGBINDIR/pg_ctl -D "$PGDATADIR" start
    while ! sudo -u $PGUSER $PGBINDIR/pg_ctl status -D $PGDATADIR | grep "server is running" -q; do
        echo "Waiting for the Postgres server to start"
    sleep 1
    done
}

stop_cluster()
{
    echo "stoping cluster ..."
    sudo -u $PGUSER $PGBINDIR/pg_ctl -D "$PGDATADIR" stop
}

create_database()
{
    echo "creating database ($DB_NAME) ..."
    sudo -u $PGUSER $PGBINDIR/createdb $DB_NAME -h /tmp -p $PGPORT $PGUSER --encoding=UTF-8 --locale=C
    TIME=`date`
    sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "comment on database $DB_NAME is 'TPC-H data, created at $TIME'"
}

init_cluster()
{
    echo "initlize cluster ..."
    if [ -d "$PGDATADIR" ]; then
        sudo -u $PGUSER rm -rf "$PGDATADIR"
    fi
    sudo -u $PGUSER mkdir -p "$PGDATADIR"
    sudo -u $PGUSER $PGBINDIR/initdb -D "$PGDATADIR" --encoding=UTF-8 --locale=C
    cat conf/postgresql.conf.settings >> $PGDATADIR/postgresql.conf
}



show_settings()
{
    sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -c "select name, current_setting(name) from pg_settings where name
    in('debug_assertions', 'wal_level', 'checkpoint_segments', 'shared_buffers', 'wal_buffers',
    'fsync', 'maintenance_work_mem', 'checkpoint_completion_target',
    'max_connections');"
}


compile_dbgen()
{
    cd "$BASEDIR/dbgen"
    if ! [ -x dbgen ] || ! [ -x qgen ];
    then
    make -j $CORES
    fi
}

create_table()
{
    echo "creating tables ..."
    sudo -u $PGUSER mkdir -p "$TPCHTMP" || die "Failed to create temporary directory: '$TPCHTMP'"
    sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME < "$BASEDIR/$1"
}

copy_data()
{
    echo "copying data ..."
    cd "$TPCHTMP"
    for f in *.tbl; do
        bf="$(basename $f .tbl)"
        echo "truncate $bf; COPY $bf FROM '$(pwd)/$f' WITH DELIMITER AS '|'" | sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME
    done
}

create_keys()
{
    echo "creating keys ..."
    # Create primary and foreign keys
    sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -f "$BASEDIR/sql/pg/create_primary_key.sql"
}
    cd "$BASEDIR"
    #sudo -u $PGUSER rm -rf "$TPCHTMP"

create_index()
{
    echo "creating indexes ..."
    sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -f "$BASEDIR/sql/pg/create_index.sql"
}


prepare_cluster()
{
    echo "preparing cluster ..."
    echo never | sudo tee /sys/kernel/mm/transparent_hugepage/defrag

    echo "Running vacuum freeze analyze..."
    sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "vacuum freeze"
    sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "analyze"
    sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME -c "checkpoint"
}

prepare_data()
{
    echo "preparing data ..."
    cd "$BASEDIR/dbgen"
    for i in $(seq 1 22);
    do
        ii=$(printf "%02d" $i)
        mkdir -p "../queries"
        DSS_QUERY=queries ./qgen $i >../queries/q$ii.sql
        sed 's/^select/explain select/' ../queries/q$ii.sql > ../queries/q$ii.explain.sql
        sed 's/^select/explain analyze select/' ../queries/q$ii.sql > ../queries/q$ii.analyze.sql
    done
}
make_data()
{
  cd "$TPCHTMP"
  sudo -u $PGUSER cp "$BASEDIR/dbgen/dists.dss" .
  sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T c 
  sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T s 
  sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T n 
  sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T r 
  sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T O 
  sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T L 
  sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T P 
  sudo -u $PGUSER "$BASEDIR/dbgen/dbgen" -s $SCALE -f -v -T S 
}

create_ch_table()
{
    clickhouse-client -d db -n < $BASEDIR/sql/ch/create_table.sql
}

t=$(timer)
init_cluster
start_cluster
create_database
if [ "$1" == "ch" ]; then
    create_ch_table
    create_table sql/fdw/clickhousedb_fdw/create_table.sql
    make_data
    copy_data
else
    create_table sql/pg/create_table.sql
    create_index
    make_data
    copy_data
    create_keys
fi
prepare_cluster
prepare_data
stop_cluster
printf 'Elapsed time: %s\n' $(timer $t)
