alter table lineitem alter  l_orderkey       set (n_distinct = 150000000);
alter table lineitem alter  l_partkey        set (n_distinct = 20000000 );
alter table lineitem alter  l_extendedprice  set (n_distinct = 5527082 );
alter table lineitem alter  l_comment        set (n_distinct = 332361703 );
alter table customer alter  c_address        set (n_distinct = 15000000 );
alter table customer alter  c_acctbal        set (n_distinct = 7605304 );
alter table customer alter  c_comment        set (n_distinct = 14963316 );
alter table orders   alter  o_totalprice     set (n_distinct = 105975267 );
alter table orders   alter  o_comment        set (n_distinct = 140248820 );
alter table part     alter  p_retailprice    set (n_distinct = 139501 );
alter table part     alter  p_comment        set (n_distinct = 7548976 );
alter table partsupp alter  ps_partkey       set (n_distinct = 20000000 );
alter table partsupp alter  ps_suppkey       set (n_distinct = 1000000 );
alter table partsupp alter  ps_supplycost    set (n_distinct = 100261 );
alter table partsupp alter  ps_comment       set (n_distinct = 79064564 );
alter table supplier alter  s_acctbal        set (n_distinct = 951918 );

