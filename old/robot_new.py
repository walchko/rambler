#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
# from js import Joystick
# from nxp_imu import IMU
# import platform
import pycreate2
from pycreate2.OI import calc_query_data_len
import time
# from mcp3208 import MCP3208
# import numpy as np
from opencvutils import Camera
from math import sqrt, atan2

"""
Body Frame

    x ^ Forward
      |
   -- |--
 /    |   \
|     +----|---> y  Right
 \        /
   ------

   z is into the page
"""


class Idle(object):
	def __init__(self, port='/dev/ttyUSB0'):
		pass

	def __del__(self):
		pass


class Create2(object):
	cr = None
	adc = None
	imu = None
	camera = None
	sensors = {}

	def __init__(self, port='/dev/ttyUSB0'):
		self.cr = pycreate2.Create2(port)
		# self.js = Joystick()
		# self.camera = Camera(cam='cv')
		# self.camera.init(win=(320, 240))

		# only create if on linux, because:
		#   imu needs access to i2c
		#   adc needs access to spi
		# if platform.system() == 'Linux':
		# 	self.imu = IMU()
		# 	self.adc = MCP3208()

	def __del__(self):
		if self.cr:
			self.cr.stop()

	def run(self):
		self.cr.start()
		self.cr.safe()

		pkts = [46, 47, 48, 49, 50, 51]
		sensor_pkt_len = calc_query_data_len(pkts)

		while True:
			# grab camera image
			# if self.camera:
			# 	ok, img = self.camera.read()
			#
			# 	if ok:  # good image capture
			# 		self.processImage(img)

			# create sensor data
			# raw = self.cr.query_list(pkts, sensor_pkt_len)
			# if raw:
			# 	for p in pkts:
			# 		self.cr.decoder.decode_packet(p, raw, self.sensors)
			# 	print('Sensors:')
			# 	print(self.sensors)

			# get joystick
			# if self.js.valid:
			# 	ps4 = self.js.get()
			# 	x, y = ps4['leftStick']
			# 	# rz, _ = ps4['rightStick']
			# # this is a default for testing if no joystick is found
			# else:
			# 	x = 1
			# 	y = 0

			# x, y = (0, 0)
			#
			# vel = sqrt(x**2 + y**2)
			# rot = atan2(x, y)  # remember, x is up not z
			# self.command(vel, rot)

			sensor_state = self.cr.get_packet(100)
			print(sensor_state)

			# read imu
			# if self.imu:
			# 	a, m, g = self.imu.read()
			# 	print('imu', a, m, g)
			#
			# # read IR sensors
			# if self.adc:
			# 	ir = self.adc.read()
			# 	print('ir', ir)

			time.sleep(0.05)

	def command(self, vel, rot, scale=1.0):
		"""
		vel: 0-1
		rot: 0-2pi
		scale: scalar multiplied to velocity
		"""
		vel *= scale

		if rot < 0.02:  # a little more than a degree
			self.cr.drive_straight(vel)
		else:
			i = int(rot*10)
			i = 0 if i < 0 else i
			i = 10 if i > 10 else i
			r = range(1100, 0, -100)
			radius = r[i]
			self.cr.drive_turn(vel, radius)
			print('cmd:', vel, radius)

	def processImage(self, img):
		# find ar code
		pass


def main():
	port = '/dev/ttyUSB0'
	bot = Create2(port)

	try:
		bot.run()

	except KeyboardInterrupt:
		print('bye ...')


if __name__ == '__main__':
	main()
