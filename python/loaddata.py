#/usr/bin/python

import time
from datetime import datetime
from multiprocessing import Process, Queue

import psycopg2

# pool size
nprocesses = 4
dbgen_path = "/home/david/pgtpch/dbgen/"
dbgen_size = "100"
db_connect_str = "dbname=tpch host=localhost"

commands = [
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 1' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 2' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 3' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 4' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 5' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 6' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 7' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 8' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 9' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 10' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 11' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 12' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 13' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 14' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 15' DELIMITER '|';",
                                "COPY lineitem FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T L -o -b " + dbgen_path + "dists.dss -C 16 -S 16' DELIMITER '|';",
                                "COPY orders FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T O -o -b " + dbgen_path + "dists.dss -C 8 -S 1' DELIMITER '|';",
                                "COPY orders FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T O -o -b " + dbgen_path + "dists.dss -C 8 -S 2' DELIMITER '|';",
                                "COPY orders FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T O -o -b " + dbgen_path + "dists.dss -C 8 -S 3' DELIMITER '|';",
                                "COPY orders FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T O -o -b " + dbgen_path + "dists.dss -C 8 -S 4' DELIMITER '|';",
                                "COPY orders FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T O -o -b " + dbgen_path + "dists.dss -C 8 -S 5' DELIMITER '|';",
                                "COPY orders FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T O -o -b " + dbgen_path + "dists.dss -C 8 -S 6' DELIMITER '|';",
                                "COPY orders FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T O -o -b " + dbgen_path + "dists.dss -C 8 -S 7' DELIMITER '|';",
                                "COPY orders FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T O -o -b " + dbgen_path + "dists.dss -C 8 -S 8' DELIMITER '|';",
                                "COPY partsupp FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T S -o -b " + dbgen_path + "dists.dss' DELIMITER '|';",
                                "COPY part FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T P -o -b " + dbgen_path + "dists.dss' DELIMITER '|';",
                                "COPY customer FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T c -o -b " + dbgen_path + "dists.dss' DELIMITER '|';",
                                "COPY supplier FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T s -o -b " + dbgen_path + "dists.dss' DELIMITER '|';",
                                "COPY nation FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T n -o -b " + dbgen_path + "dists.dss' DELIMITER '|';",
                                "COPY region FROM PROGRAM '" + dbgen_path + "dbgen -s " + dbgen_size + " -T r -o -b " + dbgen_path + "dists.dss' DELIMITER '|';"
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

