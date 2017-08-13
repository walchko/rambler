#!/usr/bin/env python

from __future__ import print_function
from __future__ import division
# from js import Joystick
# from nxp_imu import IMU
# import platform
import pycreate2
# from pycreate2.OI import calc_query_data_len
import time
# from mcp3208 import MCP3208
# import numpy as np
from opencvutils import Camera
# from math import sqrt, atan2

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

SDL: sudo apt-get install libsdl2-dev
installs this:
libasound2-dev libavahi-client-dev libavahi-common-dev libdrm-amdgpu1
libdrm-dev libdrm-exynos1 libdrm-freedreno1 libdrm-nouveau2 libdrm-omap1
libdrm-radeon1 libdrm-tegra0 libegl1-mesa libegl1-mesa-dev libelf1 libgbm1
libgl1-mesa-dev libgl1-mesa-dri libgl1-mesa-glx libglapi-mesa libgles2-mesa
libgles2-mesa-dev libglu1-mesa libglu1-mesa-dev libllvm3.9 libpulse-dev
libpulse-mainloop-glib0 libsdl2-2.0-0 libsdl2-dev libtxc-dxtn-s2tc0
libwayland-bin libwayland-client0 libwayland-cursor0 libwayland-dev
libwayland-egl1-mesa libwayland-server0 libx11-xcb-dev libxcb-dri2-0
libxcb-dri2-0-dev libxcb-dri3-0 libxcb-dri3-dev libxcb-glx0 libxcb-glx0-dev
libxcb-present-dev libxcb-present0 libxcb-randr0 libxcb-randr0-dev
libxcb-shape0-dev libxcb-sync-dev libxcb-sync1 libxcb-xfixes0-dev
libxkbcommon-dev libxkbcommon0 libxshmfence-dev libxshmfence1 libxss-dev
libxss1 libxt-dev libxt6 libxv-dev libxxf86vm-dev libxxf86vm1
mesa-common-dev x11proto-dri2-dev x11proto-gl-dev x11proto-scrnsaver-dev
x11proto-video-dev x11proto-xf86vidmode-dev

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
		self.bot = pycreate2.Create2(port)
		# self.js = Joystick()
		self.camera = Camera(cam='cv')
		self.camera.init(win=(320, 240), cameraNumber=0)

		# only create if on linux, because:
		#   imu needs access to i2c
		#   adc needs access to spi
		# if platform.system() == 'Linux':
		# 	self.imu = IMU()
		# 	self.adc = MCP3208()
		print('Start')
		print(self.bot.inputCommands([35]))

	def __del__(self):
		# if self.bot:
		# 	self.bot.stop()
		pass

	def doPath(self):
		path = [
			['forward', 200, 2, 'for'],
			['back', -200, 2, 'back'],
			['stop', 0, 0.1, 'stop'],
			['turn right', 100, 2, 'rite'],
			['turn left', -100, 4, 'left'],
			['turn right', 100, 2, 'rite'],
			['stop', 0, 0.1, 'stop']
		]

		# path to move
		for mov in path:
			# move robot
			name, vel, dt, string = mov
			print('movement:', name)
			self.bot.digit_led_ascii(string)
			if name in ['forward', 'back', 'stop']:
				self.bot.drive_straight(vel)
			elif name in ['turn right', 'turn left']:
				self.bot.drive_turn(vel, -1)
			else:
				raise Exception('invalid movement command')
				# time.sleep(0.05)
			time.sleep(dt)

	def processSafety(self, ir, wheel_drops, bumpers):
		# print('ir', ir)
		level = 200
		vel = 200
		forward = (vel, 0)
		left = (vel, 1)
		right = (vel, -1)
		dt = 0
		direction = forward
		reverse = False

		# handle wheel drops
		for danger in wheel_drops:
			if danger:
				print('crap ... lost the floor!!!')
				return (-vel, 0), 0

		# handle physical bumpers
		if bumpers[0]:
			print('bumper left: hit something on our left')
			self.bot.drive_straight(-vel)
			time.sleep(0.5)
			return right, 2
		if bumpers[1]:
			print('bumper right: hit something on our right')
			self.bot.drive_straight(-vel)
			time.sleep(0.5)
			return left, 2

		# handle light bumpers
		if ir[0] > level:
			dt = 0.5
			direction = right
			reverse = True
		if ir[1] > level:
			dt = 1.0
			direction = right
			reverse = True
		if ir[2] > level:
			dt = 1.5
			direction = right
			reverse = True
		if ir[5] > level:
			dt = 0.5
			direction = left
			reverse = True
		if ir[4] > level:
			dt = 1.0
			direction = left
			reverse = True
		if ir[3] > level:
			dt = 1.5
			direction = left
			reverse = True

		if reverse:
			self.bot.drive_straight(-vel)
			time.sleep(0.5)

		return direction, dt

	def run(self):
		print('run')
		print(self.bot.inputCommands([35]))
		self.bot.start()
		print('after start')
		print(self.bot.inputCommands([35]))
		self.bot.safe()
		print('after safe')
		print(self.bot.inputCommands([35]))
		# self.bot.full()
		exit(0)

		# health = [14, 22, 23, 24, 25, 26, 54, 55]
		# nav = [19, 20, 107]
		# safety = [7, 9, 10, 11, 12, 46, 47, 48, 49, 50, 51]

		# path = [
		# 	['forward', 200, 2, 'for'],
		# 	['back', -200, 2, 'back'],
		# 	['stop', 0, 0.1, 'stop'],
		# 	['turn right', 100, 2, 'rite'],
		# 	['turn left', -100, 4, 'left'],
		# 	['turn right', 100, 2, 'rite'],
		# 	['stop', 0, 0.1, 'stop']
		# ]

		light_bumper = [
			'light bump left signal',
			'light bump front left signal',
			'light bump center left signal',
			'light bump center right signal',
			'light bump front right signal',
			'light bump right signal',
		]

		curr_dist = 0.0

		# rn for a certain number of steps
		for _ in range(200):
			# get sensor readings
			# health_info = self.bot.inputCommands(health)
			# nav_info = self.bot.inputCommands(nav)
			# safety_info = self.bot.inputCommands(safety)
			# print('sensors:', info)
			safety_info = self.bot.inputCommands([100])  # get everything

			if not safety_info:
				exit(1)

			ir = []
			for key in light_bumper:
				ir.append(safety_info[key])

			tmp = safety_info['wheel drop and bumps']
			# print('wheel/dump', tmp)
			# wheel_drops = ((tmp & (1<<3)) > 0, (tmp & (1<<2)) > 0)  # left, right
			# bumpers = ((tmp & (1<<1)) > 0, (tmp & (1)) > 0)  # left, right

			wheel_drops = (tmp['drop left'], tmp['drop right'])
			bumpers = (tmp['bump left'], tmp['bump right'])

			direction, dt = self.processSafety(ir, wheel_drops, bumpers)

			vel = direction[0]
			if dt != 0:
				self.bot.drive_turn(vel, direction[1])
				time.sleep(dt)
			else:
				self.bot.drive_straight(vel)
				time.sleep(0.1)

			sensor_data = safety_info
			print('='*40)
			print('stasis', sensor_data['stasis'])

			curr_dist += sensor_data['distance']
			print('distance', curr_dist)
			print('-'*40)
			print('left motor current [mA]', sensor_data['left motor current'])
			print('right motor current [mA]', sensor_data['right motor current'])
			print('battery status [%]:', 100*sensor_data['battery charge']/sensor_data['battery capacity'])
			print('voltage:', sensor_data['voltage'])
			print('current:', sensor_data['current'])
			# grab camera image
			if self.camera:
				ok, img = self.camera.read()

				if ok:  # good image capture
					self.processImage(img)
				else:
					print('<<< bad image >>>')

			# time.sleep(0.5)

	def command(self, vel, rot, scale=1.0):
		"""
		vel: 0-1
		rot: 0-2pi
		scale: scalar multiplied to velocity
		"""
		vel *= scale

		if rot < 0.02:  # a little more than a degree
			self.bot.drive_straight(vel)
		else:
			i = int(rot*10)
			i = 0 if i < 0 else i
			i = 10 if i > 10 else i
			r = range(1100, 0, -100)
			radius = r[i]
			self.bot.drive_turn(vel, radius)
			print('cmd:', vel, radius)

	def processImage(self, img):
		# find ar code
		# print('image size', img.shape)
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
