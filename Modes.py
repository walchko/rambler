# The MIT License
#
# Copyright (c) 2017 Kevin Walchko

from __future__ import print_function
from __future__ import division
import time
import numpy as np
from lib.js import Joystick
from math import cos, sin, atan2, sqrt
from lib.circular_buffer import CircularBuffer


class IdleMode(object):
	def __init__(self, bot):
		self.bot = bot

	def __del__(self):
		pass

	def go(self, all_sensors):
		time.sleep(0.4)


class AutoMode(object):
	def __init__(self, bot):
		self.bot = bot

	def processSafety(self, ir, wheel_drops, bumpers):
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

	def go(self, all_sensors):
		# # grab camera image
		# if self.camera:
		# 	ok, img = self.camera.read()
		#
		# 	if ok:  # good image capture
		# 		self.processImage(img)
		# 	else:
		# 		print('<<< bad image >>>')

		# sensors = None

		# self.data['current'].push(sensors.current)
		# self.data['voltage'].push(sensors.voltage)
		# self.data['distance'].push(sensors.distance)

		sensors = all_sensors['create']

		ir_move = [-30, -60, -90, 90, 60, 30]
		ir = []
		for i in [36, 37, 38, 39, 40, 41]:
			ir.append(sensors[i])

		cliff_move = [-45, -90, 90, 45]
		cliff = []
		for i in [20, 21, 22, 23]:
			cliff.append(sensors[i])

		for s, a in zip(ir, ir_move):
			if s > 1000:
				self.bot.turn(a)

		for s, a in zip(cliff, cliff_move):
			if s < 1700:
				self.bot.turn(a)

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
	def __init__(self, bot, create2, path=None):
		self.bot = bot
		self.create = create2
		if path:
			self.path = path
		else:
			self.path = [
				['turn angle', -90, 1, 'left'],
				['turn angle', 90, 1, 'right'],
				# ['direct', (250, 250), 2, 'for'],
				# ['direct', (-250, -250), 2, 'back'],
				# ['direct', (250, -250), 2, 'rite'],
				# ['direct', (-250, 250), 2, 'left'],
				# ['forward right', (300, -500), 2, 'rite'],
				# ['reverse right', (-300, -500), 2, 'rite'],
				# ['forward left', (300, 500), 2, 'left'],
				# ['reverse left', (-300, 500), 2, 'rite'],
				# ['forward', 200, 2, 'for'],
				# ['back', -200, 2, 'back'],
				# ['stop', 0, 0.1, 'stop'],
				# ['turn right', 100, 2, 'rite'],
				# ['turn left', -100, 4, 'left'],
				# ['turn right', 100, 2, 'rite'],
				['stop', 0, 3, 'stop']
			]

	def go(self, all_sensors=None):
		"""
		Run through some pre-defined path for testing
		"""
		for mov in self.path:
			# move robot
			name, vel, dt, string = mov
			print('  movement:', name)
			self.bot.digit_led_ascii(string)
			if name in ['forward', 'back', 'stop']:
				self.bot.drive_straight(vel)
			elif name in ['turn right', 'turn left']:
				self.bot.drive_turn(vel, -1)
			elif name in ['forward right', 'forward left', 'reverse right', 'reverse left']:
				v, r = vel
				self.bot.drive_turn(v, r)
			elif name in ['direct']:
				r, l = vel
				self.bot.drive_direct(r, l)
			elif name in ['turn angle']:
				self.create.turn(vel)
			else:
				raise Exception('invalid movement command')

			time.sleep(dt)

		time.sleep(3)


class JoyStickMode(object):
	def __init__(self, bot):
		self.bot = bot
		self.js = Joystick()
		self.inv_sqrt_2 = 1/sqrt(2)
		# self.mode = ''

	def go(self, all_sensors=None):
		ps4 = self.js.get()

		if ps4.buttons[1]:  # pressed triangle
			print('Pressed triangle on PS4 ... bye!')
			exit()

		y = ps4.leftStick[1]  # y axis
		x = ps4.leftStick[0]  # x axis

		mov = self.command(x, y, 200)
		l, r = mov
		self.bot.drive_direct(l, r)  # backwards??

	def command(self, x, y, scale=1.0):
		v = sqrt(x**2 + y**2)
		phi = atan2(y, x)
		# v - max speed
		v *= scale * self.inv_sqrt_2
		speed = np.array([v, v])
		M = np.array([
			[cos(phi), -sin(phi)],
			[sin(phi), cos(phi)]
		])
		return M.dot(speed)
