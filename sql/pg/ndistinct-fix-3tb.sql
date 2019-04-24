alter table lineitem alter  l_orderkey       set (n_distinct = 4500000000);
alter table lineitem alter  l_partkey        set (n_distinct = 600000000 );
alter table lineitem alter  l_extendedprice  set (n_distinct = 140074837.6 );
alter table lineitem alter  l_comment        set (n_distinct = 9934028414 );
alter table customer alter  c_address        set (n_distinct = 450000000 );
alter table customer alter  c_acctbal        set (n_distinct = 226280448.4 );
alter table customer alter  c_comment        set (n_distinct = 448889671.6 );
alter table orders alter    o_totalprice     set (n_distinct = 3167830389 );
alter table orders alter    o_comment        set (n_distinct = 4205133387 );
alter table part alter      p_retailprice    set (n_distinct = 3613701 );
alter table part alter      p_comment        set (n_distinct = 224821164.9 );
alter table partsupp alter  ps_partkey       set (n_distinct = 600000000 );
alter table partsupp alter  ps_suppkey       set (n_distinct = 30000000 );
alter table partsupp alter  ps_supplycost    set (n_distinct = 111861 );
alter table partsupp alter  ps_comment       set (n_distinct = 2371688564 );
alter table supplier alter  s_acctbal        set (n_distinct = 28544773.56 );

