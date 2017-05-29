#!/usr/bin/env python

from __future__ import print_function
from __future__ import division

import pycreate2
from pycreate2.OI import calc_query_data_len
from pygecko.ZmqClass import Sub as zmqSub
# from pygecko.ZmqClass import Pub as zmqPub
# from pygecko import Messages as Msg
import multiprocessing as mp
# import simplejson as json
import time


class Create2(mp.Process):
	def __init__(self):
		mp.Process.__init__(self)
		self.sensors = {}

	def run(self):
		# setup create 2
		# cr = pycreate2.Create2()
		# cr.start()
		# cr.safe()
		#
		# pkts = [46, 47, 48, 49, 50, 51]
		# sensor_pkt_len = calc_query_data_len(pkts)

		# setup pygecko
		kb_sub = zmqSub(['twist_kb'], ('localhost', 9000))

		while True:
			# self.sensors = cr.query_list(pkts, sensor_pkt_len)

			topic, msg = kb_sub.recv()
			if msg:
				print('Msg:', msg)

			if True:
				print('Sensors:')
				print(self.sensors)

			time.sleep(0.5)


class Camera(object):
	def __init__(self):
		pass




def main():
	bot = Create2()
	bot.run()


if __name__ == '__main__':
	main()
