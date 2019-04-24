#!/bin/bash

###
# This script runs all the queries individually
#   * 1) Gather execution time using '/usr/bin/time'
#   * 2) Collect data with perf to generate callgraph
#   * 3) Collect a set of basic statistics, again using perf. For now we obtain
#     the default given by perf, but this can be modified later to extract
#     statistics of interest to us.
###

DB_NAME=tpch
PERFDATADIR=/home/david/pgtpch/results

BASEDIR=$(dirname "$0")
BASEDIR=$(cd "$BASEDIR"; pwd)

dir="$PERFDATADIR"
mkdir -p $dir
psql $DB_NAME -c "select relname,pg_relation_size(oid) as relation_size,pg_total_relation_size(oid) as total_size,pg_size_pretty(pg_relation_size(oid)) as pretty_rel_size,pg_size_pretty(pg_total_relation_size(oid)) as pretty_total_size from pg_class where relname in('customer','lineitem','nation','orders','part','partsupp','region','supplier') order by relname;" > "$dir/rel_sizes.txt"


for i in $(seq 1 22);
#for i in $(seq 1 22);
do
  echo "Running query (EXPLAIN): $i"

  ii=$(printf "%02d" $i)
  dir="$PERFDATADIR/q${ii}"
  mkdir -p $dir
  cd "$dir"
  chmod 777 .

  f="queries/q$ii.explain.sql"

  ### Execute query with explain to get query plan
  echo "Execute query with explain to get query plan"
  psql $DB_NAME -c "\i $BASEDIR/$f" > explain.txt

done

for i in $(seq 1 22);
do
  echo "Running query (EXEC): $i"

  ii=$(printf "%02d" $i)
  dir="$PERFDATADIR/q${ii}"
  mkdir -p $dir
  cd "$dir"
  chmod 777 .

  f="queries/q$ii.sql"

  ### Get execution time without perf
  /usr/bin/time -f '%e\n%Uuser %Ssystem %Eelapsed %PCPU (%Xtext+%Ddata %Mmax)k' \
    psql -d $DB_NAME > /dev/null 2> exectime.txt <<EOF
set statement_timeout=86400000;
\i $BASEDIR/$f
EOF

done

for i in $(seq 1 22);
do
  echo "Running query (EXPLAIN ANALYZE): $i"

  ii=$(printf "%02d" $i)
  dir="$PERFDATADIR/q${ii}"
  mkdir -p $dir
  cd "$dir"
  chmod 777 .

  f="queries/q$ii.analyze.sql"

  ### Execute query with explain analyze to get query plan
  echo "Execute query with explain analyze to get query plan"
  psql -d $DB_NAME > /dev/null 2> analyze.txt <<EOF
set statement_timeout=86400000;
\i $BASEDIR/$f
EOF

done
