#!/bin/bash

###
# This script runs a single query
#   * 1) Gather execution time using '/usr/bin/time'
#   * 2) Collect data with perf to generate callgraph
#   * 3) Collect a set of basic statistics, again using perf. For now we obtain
#     the default given by perf, but this can be modified later to extract
#     statistics of interest to us.
###

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)
. "$BASEDIR/pgtpch_defaults"

if [ $# -lt 1 ]; then
  echo "Please provide the number of the query you wish to run, e.g.:"
  echo "$0 6 [dir-sufix]"
  exit 1
fi

# Set up a custom directory for this query run
PERFDATADIR="$PERFDATADIR-${SCALE}GB"
if [ $# -eq 2 ]; then
  PERFDATADIR="$PERFDATADIR-$2"
fi

perf_set_kernel_params

# Start a new instance of Postgres
sudo -u $PGUSER taskset -c 2 $PGBINDIR/postgres -D "$PGDATADIR" -p $PGPORT &
PGPID=$!
while ! sudo -u $PGUSER $PGBINDIR/pg_ctl status -D $PGDATADIR | grep "server is running" -q; do
  echo "Waiting for the Postgres server to start"
  sleep 1
done

# wait for it to finish starting
sleep 5
echo "Postgres running, pid $PGPID"

ii=$(printf "%02d" $1)
dir="$PERFDATADIR/q${ii}"
mkdir -p $dir
cd "$dir"
chmod 777 .

### Query to be executed
f="queries/q$ii.sql"
fe="queries/q$ii.explain.sql"
fa="queries/q$ii.analyze.sql"

### Execute query with explain analyze to get query plan
echo "Execute query with explain analyze to get query plan"
sudo -u $PGUSER $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME <"$BASEDIR/$fa" > analyze.txt
restart_drop_caches

### Collect data with perf to generate callgraph
echo "Collect data with perf to generate callgraph"
/usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k'\
  sudo -u $PGUSER perf record -a -C 2 -s -g -m 512 --\
  $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME <"$BASEDIR/$f" 2> exectime.txt
restart_drop_caches

### Collect basic stats with perf
echo "Collect basic stats with perf"
sudo -u $PGUSER perf stat -a -C 2 -B --log-fd 2 --\
  $PGBINDIR/psql -h /tmp -p $PGPORT -d $DB_NAME <"$BASEDIR/$f" 2> stats.txt
restart_drop_caches

sudo chown $USER:$USER *
chmod 775 .

cgf="../q${ii}-callgraph.pdf"
echo "Creating the call graph: $cgf"
perf script | python "$BASEDIR/gprof2dot.py" -f perf | dot -Tpdf -o $cgf &

# Statistics collection
  perf script | python "$BASEDIR/gprof2dot.py" -f perf | python "$BASEDIR/collect_stats.py" $i > q${ii}-breakdown.csv

cd - >/dev/null

# Stop the server
sudo -u $PGUSER $PGBINDIR/pg_ctl stop -D $PGDATADIR

for p in $(jobs -p);
do
  wait $p
done

