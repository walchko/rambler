#!/usr/bin/env python
# The MIT License
#
# Copyright (c) 2017 Kevin Walchko

from __future__ import print_function
from __future__ import division
# from js import Joystick
from nxp_imu import IMU
import platform
import pycreate2
import time
# import numpy as np
from opencvutils import Camera
# from math import sqrt, atan2
from lib.circular_buffer import CircularBuffer
import sparkline
# from lib.js import Joystick
# from lib.js import PS4

from Modes import AutoMode, DemoMode, IdleMode, JoyStickMode


"""
IMU Frame

       x ^ Forward
         |
      -- |--
y   /    |   \
<--|-----+    |
    \        /
      ------

   z is out of the page


"""


class DataRecorder(object):
	def __init__(self, filename):
		self.filename = filename

	def __del__(self):
		pass

	def save(self):
		pass





class Create2(object):
	cr = None
	adc = None
	imu = None
	camera = None
	sensors = {}

	def __init__(self, port='/dev/ttyUSB0'):
		self.bot = pycreate2.Create2(port)
		self.camera = Camera(cam='cv')
		self.camera.init(win=(320, 240), cameraNumber=0)

		# only create if on linux, because:
		#   imu needs access to i2c
		#   adc needs access to spi
		if platform.system() == 'Linux':
			self.imu = IMU()
		print('Start Create2')
		# num = 50
		# self.data = {
		# 	'current': CircularBuffer(num),
		# 	'distance': CircularBuffer(num),
		# 	'voltage': CircularBuffer(num),
		# }

		self.modes = {
			'js': JoyStickMode(self.bot),
			'demo': DemoMode(self.bot),
			'auto': AutoMode(self.bot),
			'idle': IdleMode(self.bot)
		}

		self.current_mode = 'idle'

	def __del__(self):
		self.current_mode = 'idle'

		# for k, v in self.data.items():
		# 	# print(k, sparkline.sparkify(v.get_all()).encode('utf-8'))
		# 	print(u'{} [{},{}]: {}'.format(k, v.min, v.max, sparkline.sparkify(v.get_all()).encode('utf-8')))
		print('Create2 robot is exiting ...')

	def setMode(self, mode):
		if mode in self.modes:
			self.current_mode = mode
		else:
			raise Exception('Create2::setMode selected mode is invalid: {}'.format(mode))

	def run(self):
		# print('run')
		self.bot.start()
		# print('start')
		self.bot.safe()
		# print('safe')
		# self.bot.full()

		# self.setMode('js')
		self.setMode('demo')

		while True:
			# control roobma
			self.modes[self.current_mode].go()
			time.sleep(0.1)

	def processImage(self, img):
		pass

	def printInfo(self):
		# sensor_data = safety_info
		# print('='*40)
		# print('stasis', sensor_data['stasis'])
		#
		# curr_dist += sensor_data['distance']
		# print('distance', curr_dist)
		# print('-'*40)
		# print('left motor current [mA]', sensor_data['left motor current'])
		# print('right motor current [mA]', sensor_data['right motor current'])
		# print('battery status [%]:', 100*sensor_data['battery charge']/sensor_data['battery capacity'])
		# print('voltage:', sensor_data['voltage'])
		# print('current:', sensor_data['current'])
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
