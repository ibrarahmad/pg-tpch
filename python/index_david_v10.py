#/usr/bin/python

import time
from datetime import datetime
from multiprocessing import Process, Queue

import psycopg2

# pool size
nprocesses = 4 
db_connect_str = "dbname=tpch host=localhost"


commands = [
"CREATE INDEX customer_c_mktsegment_c_custkey_idx ON customer (c_mktsegment, c_custkey) WITH (fillfactor = 100);",
"CREATE INDEX customer_c_nationkey_c_custkey_idx ON customer (c_nationkey, c_custkey) WITH (fillfactor = 100);",
"CREATE INDEX customer_ios_test1 ON customer (substring(c_phone from 1 for 2), c_acctbal, c_custkey) WITH (fillfactor = 100);",
"CREATE UNIQUE INDEX pk_customer ON customer (c_custkey) WITH (fillfactor = 100);",
"CREATE INDEX line_item_l_orderkey_l_suppkey_idx ON lineitem (l_orderkey, l_suppkey) WITH (fillfactor = 100) TABLESPACE fast_random_access;",
"CREATE INDEX lineitem_l_orderkey_idx_l_returnflag ON lineitem (l_orderkey) WITH (fillfactor = 100) WHERE l_returnflag = 'R';",
"CREATE INDEX lineitem_l_orderkey_idx_part1 ON lineitem (l_orderkey, l_suppkey) WITH (fillfactor = 100) WHERE l_commitdate < l_receiptdate; -- Q4,Q21",
"CREATE INDEX lineitem_l_orderkey_idx_part2 ON lineitem (l_orderkey) WITH (fillfactor = 100) WHERE l_commitdate < l_receiptdate AND l_shipdate < l_commitdate;",
"CREATE INDEX lineitem_l_partkey_l_quantity_l_shipmode_idx ON lineitem (l_partkey, l_quantity, l_shipmode) WITH (fillfactor = 100);",
"CREATE INDEX lineitem_l_partkey_l_suppkey_l_shipdate_l_quantity_idx ON lineitem (l_partkey, l_suppkey, l_shipdate, l_quantity) WITH (fillfactor = 100);",
"CREATE INDEX lineitem_l_shipdate_idx ON lineitem USING BRIN (l_shipdate);",
"CREATE INDEX lineitem_l_receiptdate_idx ON lineitem USING BRIN (l_receiptdate);",
"CREATE UNIQUE INDEX pk_lineitem ON lineitem (l_orderkey, l_linenumber) WITH (fillfactor = 100);",
"CREATE UNIQUE INDEX pk_nation ON nation (n_nationkey) WITH (fillfactor = 100);",
"CREATE INDEX orders_o_custkey_idx ON orders (o_custkey) WITH (fillfactor = 100);",
"CREATE INDEX orders_o_orderkey_o_orderdate_idx ON orders (o_orderkey, o_orderdate) WITH (fillfactor = 100);",
"CREATE INDEX orders_o_orderdate_idx ON orders USING BRIN (o_orderdate);",
"CREATE UNIQUE INDEX pk_orders ON orders (o_orderkey) WITH (fillfactor = 100);",
"CREATE INDEX part_ios_test1 ON part USING btree (p_size, p_partkey, p_brand, p_type) WITH (fillfactor = 100);",
"CREATE INDEX part_p_container_p_brand_p_partkey_idx ON part(p_container, p_brand, p_partkey) WITH (fillfactor = 100);",
"CREATE INDEX part_p_size_idx ON part USING BRIN (p_size);",
"CREATE INDEX part_p_type_p_partkey_idx ON part(p_type, p_partkey) WITH (fillfactor = 100);",
"CREATE UNIQUE INDEX pk_part ON part (p_partkey) WITH (fillfactor = 100);",
"CREATE INDEX partsupp_ps_suppkey_idx ON partsupp (ps_suppkey) WITH (fillfactor = 100);",
"CREATE UNIQUE INDEX pk_partsupp ON partsupp (ps_partkey, ps_suppkey) WITH (fillfactor = 100);",
"CREATE UNIQUE INDEX pk_region ON region (r_regionkey) WITH (fillfactor = 100);",
"CREATE UNIQUE INDEX pk_supplier ON supplier (s_suppkey) WITH (fillfactor = 100);",
"CREATE INDEX supplier_s_nationkey_s_suppkey_idx ON supplier (s_nationkey, s_suppkey) WITH (fillfactor = 100);",
"CREATE INDEX supplier_s_suppkey_idx_like ON supplier (s_suppkey) WITH (fillfactor = 100) WHERE s_comment LIKE '%Customer%Complaints%';"
]


def run_commands(i, queue_in, queue_out):

		try:

				conn = psycopg2.connect(db_connect_str)
				cur  = conn.cursor()

				# iterate over results from the queue
				while True:

						# by default we have nothing
						sql = None

						try:
								sql = queue_in.get_nowait()
						except:
							pass

						if sql is None:
							break

						# build the SQL query
						queue_out.put({'type' : 'START', 'time' : datetime.now().strftime('%y-%m-%d %H:%M:%S'), 'sql' : sql})

						start_time = time.time()

						cur.execute(sql)
						conn.commit()

						end_time = time.time()

						# put the output message
						queue_out.put({'type' : 'END', 'time' : datetime.now().strftime('%y-%m-%d %H:%M:%S'), 'sql' : sql, 'duration' : int(end_time - start_time)})

				# close the cursor/connection
				cur.close()
				conn.close()

		except Exception as ex:

				print "process %(id)s failed: %(msg)s" % {'id' : str(i), 'msg' : str(ex)}


def receive_messages(q):
		'receive messages'

		while True:

				m = q.get(True)

				# we only know EXIT and START/END messages

				if m['type'] == 'EXIT':
						break

				elif m['type'] == 'START':
						print "%(time)s %(type)s %(sql)s" % m

				elif m['type'] == 'END':
						print "%(time)s %(type)s %(sql)s %(duration)s" % m


if __name__ == '__main__':

		# input queue (with all the files to print)
		queue_in = Queue()

		# fill the queue (all the commands at once)
		[queue_in.put(c) for c in commands]

		# output messages (not to print garbage)
		queue_out = Queue()

		# create pool of the expected size
		workers = [Process(target=run_commands, args=(i,queue_in,queue_out)) for i in range(nprocesses)]

		# create the process printing messages
		printer = Process(target=receive_messages, args=(queue_out,))

		# start all the workers and printer thread
		[p.start() for p in workers]
		printer.start()

		# wait for all the workers to complete
		[p.join() for p in workers]

		# terminate the message receiver (send message, wait for termination)
		queue_out.put({'type' : 'EXIT'})
		printer.join()

