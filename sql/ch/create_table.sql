DROP TABLE IF EXISTS supplier;
DROP TABLE IF EXISTS part;
DROP TABLE IF EXISTS partsupp;
DROP TABLE IF EXISTS customer;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS lineitem;
DROP TABLE IF EXISTS nation;
DROP TABLE IF EXISTS region;
 
CREATE TABLE supplier (
        s_suppkey  INTEGER,
        s_name VARCHAR,
        s_address VARCHAR,
        s_nationkey INTEGER,
        s_phone VARCHAR,
        s_acctbal float,
        s_comment VARCHAR
) ENGINE = MergeTree PARTITION BY s_suppkey ORDER BY tuple();

CREATE TABLE part (
        p_partkey INTEGER,
        p_name VARCHAR,
        p_mfgr VARCHAR,
        p_brand VARCHAR,
        p_type VARCHAR,
        p_size INTEGER,
        p_container VARCHAR,
        p_retailprice float,
        p_comment VARCHAR
) ENGINE = MergeTree PARTITION BY p_partkey ORDER BY tuple();

CREATE TABLE partsupp (
        ps_partkey INTEGER,
        ps_suppkey INTEGER,
        ps_availqty INTEGER,
        ps_supplycost float,
        ps_comment VARCHAR
) ENGINE = MergeTree PARTITION BY ps_partkey ORDER BY tuple();

CREATE TABLE customer (
        c_custkey INTEGER,
        c_name VARCHAR,
        c_address VARCHAR,
        c_nationkey INTEGER,
        c_phone VARCHAR,
        c_acctbal float,
        c_mktsegment VARCHAR,
        c_comment VARCHAR
) ENGINE = MergeTree PARTITION BY c_custkey ORDER BY tuple();

CREATE TABLE orders (
        o_orderkey BIGINT,
        o_custkey INTEGER,
        o_orderstatus VARCHAR,
        o_totalprice float,
        o_orderdate DATE,
        o_orderpriority VARCHAR,
        o_clerk VARCHAR,
        o_shippriority INTEGER,
        o_comment VARCHAR
) ENGINE = MergeTree PARTITION BY o_orderkey ORDER BY tuple();

CREATE TABLE lineitem (
        l_orderkey BIGINT,
        l_partkey INTEGER,
        l_suppkey INTEGER,
        l_linenumber INTEGER,
        l_quantity float,
        l_extendedprice float,
        l_discount float,
        l_tax float,
        l_returnflag VARCHAR,
        l_linestatus VARCHAR,
        l_shipdate DATE,
        l_commitdate DATE,
        l_receiptdate DATE,
        l_shipinstruct VARCHAR,
        l_shipmode VARCHAR,
        l_comment VARCHAR
) ENGINE = MergeTree PARTITION BY l_orderkey ORDER BY tuple();

CREATE TABLE nation (
        n_nationkey INTEGER,
        n_name VARCHAR,
        n_regionkey INTEGER,
        n_comment VARCHAR
) ENGINE = MergeTree PARTITION BY n_nationkey ORDER BY tuple();

CREATE TABLE region (
        r_regionkey INTEGER,
        r_name VARCHAR,
        r_comment VARCHAR
) ENGINE = MergeTree PARTITION BY r_regionkey ORDER BY tuple();

