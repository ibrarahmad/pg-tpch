#/usr/bin/python

import time
from datetime import datetime
from multiprocessing import Process, Queue

import psycopg2

# pool size
nprocesses = 16
db_connect_str = "dbname=tpch host=localhost"


commands = [
"ALTER TABLE nation ADD CONSTRAINT nation_n_regionkey_fkey FOREIGN KEY (n_regionkey) REFERENCES region(r_regionkey)",
"ALTER TABLE supplier ADD CONSTRAINT supplier_s_nationkey_fkey FOREIGN KEY (s_nationkey) REFERENCES nation(n_nationkey)",
"ALTER TABLE partsupp ADD CONSTRAINT partsupp_ps_partkey_fkey FOREIGN KEY (ps_partkey) REFERENCES part(p_partkey)",
"ALTER TABLE partsupp ADD CONSTRAINT partsupp_ps_suppkey_fkey FOREIGN KEY (ps_suppkey) REFERENCES supplier(s_suppkey)",
"ALTER TABLE lineitem ADD CONSTRAINT lineitem_l_suppkey_l_partkey_fkey FOREIGN KEY (l_partkey, l_suppkey) REFERENCES partsupp (ps_partkey, ps_suppkey);",
"ALTER TABLE customer ADD CONSTRAINT customer_c_nationkey_fkey FOREIGN KEY (c_nationkey) REFERENCES nation(n_nationkey)",
"ALTER TABLE orders ADD CONSTRAINT orders_o_custkey_fkey FOREIGN KEY (o_custkey) REFERENCES customer(c_custkey)",
"ALTER TABLE lineitem ADD CONSTRAINT lineitem_l_orderkey_fkey FOREIGN KEY (l_orderkey) REFERENCES orders(o_orderkey)",
"ALTER TABLE lineitem ADD CONSTRAINT lineitem_l_partkey_fkey FOREIGN KEY (l_partkey) REFERENCES part(p_partkey)",
"ALTER TABLE lineitem ADD CONSTRAINT lineitem_l_suppkey_fkey FOREIGN KEY (l_suppkey) REFERENCES supplier(s_suppkey)"
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

