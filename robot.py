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
from pprint import pprint

"""
key-wakeup\r\n'
slept for 0 minutes 32 seconds\r\n\r\n
2015-08-24-1648-L   \r\n
r3-robot/tags/release-3.5.x-tags/release-3.5.4:6058 CLEAN\r\n\r\n
bootloader id: 4718 6549 82EC CFFF \r\n
assembly: 3.5-lite-batt\r\n
revision: 2\r\n
flash version: 10\r\nflash info crc passed: 1\r\n\r\n
battery-current-zero 257\r']
"""


class Create2(mp.Process):
	def __init__(self):
		mp.Process.__init__(self)
		self.sensors = {}
		self.cr = None

	def __del__(self):
		# self.cr.stop()
		pass

	def run(self):
		# setup create 2
		port = '/dev/ttyUSB0'
		self.cr = pycreate2.Create2(port)
		self.cr.start()
		self.cr.safe()

		pkts = [46, 47, 48, 49, 50, 51]
		sensor_pkt_len = calc_query_data_len(pkts)

		# setup pygecko
		kb_sub = zmqSub(['twist_kb'], ('192.168.1.8', 9000), hwm=20)

		while True:
			raw = self.cr.query_list(pkts, sensor_pkt_len)

			topic, msg = kb_sub.recv()
			if msg:
				# print('Msg:', msg)
				vel = msg.linear.x
				rot = msg.angular.z
				print('raw', vel, rot)

				if rot == 0.0:
					# self.cr.drive_straight(vel)
					pass
				else:
					i = int(rot*10)
					i = 0 if i < 0 else i
					i = 10 if i > 10 else i
					r = range(1100, 0, -100)
					radius = r[i]
					# self.cr.drive_turn(vel, radius)
					print('cmd:', vel, radius)
			else:
				print('no command')

			# if raw:
			# 	for p in pkts:
			# 		self.cr.decoder.decode_packet(p, raw, self.sensors)
			# 	print('Sensors:')
			# 	pprint(self.sensors)
			# else:
			# 	print('robot asleep')

			# time.sleep(0.05)


class Camera(object):
	def __init__(self):
		pass

	def run(self):
		while True:
			print('camera')
			time.sleep(3)


def main():
	bot = Create2()
	cam = Camera()

	try:
		bot.start()

		cam.run()

		bot.join()

	except KeyboardInterrupt:
		if bot.is_alive():
			print('*** Terminating bot ***')
			bot.terminate()


if __name__ == '__main__':
	main()
