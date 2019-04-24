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
