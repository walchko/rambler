#!/usr/bin/env python

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
from lib.js import Joystick
# from lib.js import PS4


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


class IdleMode(object):
	def __init__(self, bot):
		self.bot = bot

	def __del__(self):
		pass

	def go(self):
		sleep(1)


class AutoMode(object):
	def __init__(self, bot):
		self.bot = bot

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

	def go(self):
		sensors = None
		while not sensors:
			try:
				print('No sensor info, is robot asleep????')
				# time.sleep(1)
				sensors = self.bot.inputCommands()  # get everything
			except Exception:
				continue

		self.data['current'].push(sensors.current)
		self.data['voltage'].push(sensors.voltage)
		self.data['distance'].push(sensors.distance)

		ir = []
		for i in [36, 37, 38, 39, 40, 41]:
			ir.append(sensors[i])

		wheel_drops = (sensors.bumps_wheeldrops.wheeldrop_left, sensors.bumps_wheeldrops.wheeldrop_right)
		bumpers = (sensors.bumps_wheeldrops.bump_left, sensors.bumps_wheeldrops.bump_right)

		direction, dt = self.processSafety(ir, wheel_drops, bumpers)

		vel = direction[0]
		if dt != 0:
			self.bot.drive_turn(vel, direction[1])
			time.sleep(dt)
		else:
			self.bot.drive_straight(vel)
			time.sleep(0.1)


class DemoMode(object):
	def __init__(self, bot, path=None):
		self.bot = bot
		if path:
			self.path = path
		else:
			self.path = [
				['forward', 200, 2, 'for'],
				['back', -200, 2, 'back'],
				['stop', 0, 0.1, 'stop'],
				['turn right', 100, 2, 'rite'],
				['turn left', -100, 4, 'left'],
				['turn right', 100, 2, 'rite'],
				['stop', 0, 0.1, 'stop']
			]

	def go(self):
		"""
		Run through some pre-defined path for testing
		"""
		for mov in self.path:
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

			time.sleep(dt)

		time.sleep(3)


class JoyStickMode(object):
	def __init__(self, bot):
		self.bot = bot
		js = Joystick()

	def go(self):
		ps4 = js.get()
		x = ps4.leftStick[0]
		y = ps4.leftStick[1]

		print(x,y)


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
		if platform.system() == 'Linux':
			self.imu = IMU()
		# 	self.adc = MCP3208()
		print('Start')
		# print(self.bot.inputCommands([35]))
		num = 50
		self.data = {
			'current': CircularBuffer(num),
			'distance': CircularBuffer(num),
			'voltage': CircularBuffer(num),
		}

		self.modes = {
			'js': JoyStickMode(self.bot),
			'demo': DemoMode(self.bot),
			'auto': AutoMode(self.bot),
			'idle': IdleMode(self.bot)
		}

		self.current_mode = 'idle'

	def __del__(self):
		self.current_mode = 'idle'

		for k, v in self.data.items():
			# print(k, sparkline.sparkify(v.get_all()).encode('utf-8'))
			print(u'{} [{},{}]: {}'.format(k, v.min, v.max, sparkline.sparkify(v.get_all()).encode('utf-8')))
		print('Create2 robot is exiting ...')

	def setMode(self, mode):
		if mode in self.modes:
			self.current_mode = mode
		else:
			raise Exception('Create2::setMode selected mode is invalid: {}'.format(mode))

	def run(self):
		print('run')
		# print(self.bot.inputCommands([35]))
		self.bot.start()
		print('after start')
		# print(self.bot.inputCommands([35]))
		self.bot.safe()
		print('after safe')
		# print(self.bot.inputCommands([35]))
		# self.bot.full()

		# curr_dist = 0.0

		self.setMode('demo')

		# run for a certain number of steps
		for _ in range(20):
			# get commands
			self.modes[self.current_mode]
			# get sensor readings

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
