#!/usr/bin/env python
# The MIT License
#
# Copyright (c) 2017 Kevin Walchko

from __future__ import print_function
from __future__ import division
from nxp_imu import IMU
import platform
import pycreate2
import time
# import numpy as np
from opencvutils import Camera
# from math import sqrt, atan2
# from lib.circular_buffer import CircularBuffer
import sparkline
from lib.bagit import Bag
from Modes import AutoMode, DemoMode, IdleMode, JoyStickMode
from ins_nav import AHRS
from ins_nav.utils import quat2euler
from lib.circular_buffer import CircularBuffer


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


class Create2(object):
	bot = None
	imu = None
	camera = None
	sensors = {}

	def __init__(self, port='/dev/ttyUSB0'):
		self.bot = pycreate2.Create2(port)

		# only create if on linux:
		image_size = (640, 480)
		if platform.system() == 'Linux':
			self.camera = Camera(cam='pi')
			self.camera.init(win=image_size)
			self.imu = IMU()
		else:
			self.camera = Camera(cam='cv')
			self.camera.init(win=image_size, cameraNumber=0)

		self.sensors = {'create': None, 'imu': None, 'camera': None}

		self.distance = 0.0

		self.ahrs = AHRS()

		self.modes = {
			'js': JoyStickMode(self.bot),
			'demo': DemoMode(self.bot, self),
			'auto': AutoMode(self.bot),
			'idle': IdleMode(self.bot)
		}

		# self.bag = Bag('./data/robot-{}.json'.format(time.ctime().replace(' ', '-')), ['imu', 'camera', 'create'])

		self.current_mode = 'idle'

		self.last_time = time.time()

		self.data = {
			# 'r': CircularBuffer(30),
			# 'p': CircularBuffer(30),
			'y': CircularBuffer(30),
		}

	def __del__(self):
		# self.bag.close()
		self.bot.drive_direct(0, 0)
		self.current_mode = 'idle'
		print('Create2 robot is exiting ...')

	def setMode(self, mode):
		if mode in self.modes:
			self.current_mode = mode
		else:
			raise Exception('Create2::setMode selected mode is invalid: {}'.format(mode))

	def run(self):
		self.bot.start()
		self.bot.safe()
		# self.bot.full()

		# self.setMode('js')
		self.setMode('demo')
		# self.setMode('idle')
		# self.setMode('auto')

		while True:
			self.get_sensors()
			self.printInfo()
			# control roobma
			self.modes[self.current_mode].go(self.sensors)
			time.sleep(0.1)

	def processImage(self, img):
		pass

	def turn(self, angle, speed=100):
		"""
		Uses the encoders to turn an angle in degrees. This is a best effort,
		the results will not be perfect due to wheel sleep and encoder errors.

		CCW is positive
		CW is negative
		"""
		self.get_sensors()
		turn_angle = 0.0

		if angle > 0:
			cmd = (speed, -speed)  # R, L
			scale = -1
		else:
			cmd = (-speed, speed)
			scale = 1

		while abs(turn_angle) < abs(angle):
			self.bot.drive_direct(*cmd)
			self.get_sensors()
			sensors = self.sensors['create']
			turn_angle += sensors.angle

	def printInfo(self):
		sensors = self.sensors['create']
		imu = self.sensors['imu']

		if sensors is None or imu is None:
			print('No valid sensor info')
			return

		a, m, g = imu
		now = time.time()
		dt = self.last_time - now
		beta = 0.5
		q = self.ahrs.updateAGM(a, m, g, beta, dt)
		r, p, y = quat2euler(q)

		# self.data['r'].push(r)
		# self.data['p'].push(p)
		self.data['y'].push(y)

		self.last_time = now

		ir = []
		for i in [36, 37, 38, 39, 40, 41]:
			ir.append(sensors[i])

		cliff = []
		for i in [20, 21, 22, 23]:
			cliff.append(sensors[i])

		po = [
			'--------------------------------------------------------',
			'  Light Bumper: {:6} {:6} {:6} L| {:6} |R {:6} {:6} {:6}'.format(
				sensors.light_bumper_left,
				sensors.light_bumper_front_left,
				sensors.light_bumper_center_left,
				sparkline.sparkify(ir).encode('utf-8'),
				sensors.light_bumper_center_right,
				sensors.light_bumper_front_right,
				sensors.light_bumper_right
			),
			'  Cliff: {:6} {:6} L| {:4} |R {:6} {:6}'.format(
				sensors.cliff_left_signal,
				sensors.cliff_front_left_signal,
				sparkline.sparkify(cliff).encode('utf-8'),
				sensors.cliff_front_right_signal,
				sensors.cliff_right_signal
			),
			'  Encoders: {:7} L|R {:7}'.format(sensors.encoder_counts_left, sensors.encoder_counts_right),
			'  Distance Delta: {:8} mm  Total: {:10.1f} m'.format(sensors.distance, self.distance),
			'  Yaw: {:8.1f} {:30} degrees'.format(self.data['y'].get_last(), self.data['y'].spark()),
			'--------------------------------------------------------',
			'  Power: {:6} mAhr [{:3} %]'.format(sensors.battery_charge, int(100.0*sensors.battery_charge/sensors.battery_capacity)),
			'  Voltage: {:7.1f} V    Current: {:7.1f} A'.format(sensors.voltage/1000, sensors.current/1000)
		]

		for s in po:
			print(s)

	def get_sensors(self):
		cr = self.bot.get_sensors()
		self.sensors['create'] = cr
		# self.bag.push('create', cr)

		imu = self.imu.get()
		self.sensors['imu'] = imu
		# self.bag.push('imu', imu)

		self.distance += cr.distance/1000.0

		self.sensors['camera'] = None
		if self.sensors['camera']:
			ret, img = self.camera.read()
			if ret:
				self.sensors['camera'] = img
				# self.bag.push('camera', img, True)
				self.processImage(img)


def main():
	port = '/dev/ttyUSB0'
	bot = Create2(port)

	try:
		bot.run()

	except KeyboardInterrupt:
		print('bye ...')

	except Exception as e:
		print('Something else happened ... :(')
		print(e)


if __name__ == '__main__':
	main()
