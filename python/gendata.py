#/usr/bin/python

import time
from datetime import datetime
from multiprocessing import Process, Queue

import os

# pool size
nprocesses = 8
dbgen_path = "/home/david/pgtpch/dbgen/"
dbgen_size = "100"


commands = [
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 1",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 2",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 3",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 4",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 5",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 6",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 7",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 8",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 9",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 10",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 11",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 12",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 13",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 14",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 15",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T L -b " + dbgen_path + "dists.dss -C 16 -S 16",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T O -b " + dbgen_path + "dists.dss -C 8 -S 1",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T O -b " + dbgen_path + "dists.dss -C 8 -S 2",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T O -b " + dbgen_path + "dists.dss -C 8 -S 3",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T O -b " + dbgen_path + "dists.dss -C 8 -S 4",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T O -b " + dbgen_path + "dists.dss -C 8 -S 5",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T O -b " + dbgen_path + "dists.dss -C 8 -S 6",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T O -b " + dbgen_path + "dists.dss -C 8 -S 7",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T O -b " + dbgen_path + "dists.dss -C 8 -S 8",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T S -b " + dbgen_path + "dists.dss",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T P -b " + dbgen_path + "dists.dss",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T c -b " + dbgen_path + "dists.dss",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T s -b " + dbgen_path + "dists.dss",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T n -b " + dbgen_path + "dists.dss",
                                dbgen_path + "dbgen -s " + dbgen_size + " -T r -b " + dbgen_path + "dists.dss"
]


def run_commands(i, queue_in, queue_out):

		try:

				# iterate over results from the queue
				while True:

						# by default we have nothing
						cmd = None

						try:
								cmd = queue_in.get_nowait()
						except:
							pass

						if cmd is None:
							break

						# build the SQL query
						queue_out.put({'type' : 'START', 'time' : datetime.now().strftime('%y-%m-%d %H:%M:%S'), 'cmd' : cmd})

						start_time = time.time()

						os.system(cmd)

						end_time = time.time()

						# put the output message
						queue_out.put({'type' : 'END', 'time' : datetime.now().strftime('%y-%m-%d %H:%M:%S'), 'cmd' : cmd, 'duration' : int(end_time - start_time)})


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

