from __future__ import print_function
from __future__ import division
# from js import Joystick
from nxp_imu import IMU
# import platform
# import pycreate2
import time
# import numpy as np
from opencvutils import Camera
from math import sqrt, atan2, pi
# from lib.circular_buffer import CircularBuffer
# import sparkline
from lib.js import Joystick


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
		# # grab camera image
		# if self.camera:
		# 	ok, img = self.camera.read()
		#
		# 	if ok:  # good image capture
		# 		self.processImage(img)
		# 	else:
		# 		print('<<< bad image >>>')

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
				['forward right', (300, -500), 2, 'rite'],
				['reverse right', (-300, -500), 2, 'rite'],
				['forward left', (300, 500), 2, 'left'],
				['reverse left', (-300, 500), 2, 'rite'],
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
			elif name in ['forward right', 'forward left', 'reverse right', 'reverse left']:
				v, r = vel
				self.bot.drive_turn(v, r)
			else:
				raise Exception('invalid movement command')

			time.sleep(dt)

		time.sleep(3)


class JoyStickMode(object):
	def __init__(self, bot):
		self.bot = bot
		self.js = Joystick()

	def go(self):
		ps4 = self.js.get()

		if ps4.buttons[1]:  # pressed triangle
			print('Pressed triangle on PS4 ... bye!')
			exit()

		y = ps4.leftStick[1]  # y axis - turn
		x = ps4.rightStick[0]  # x axis - straight

		# sgn = 1 if x > 0 else -1
		# mag = sqrt(x**2 + y**2)*sgn
		# angle = atan2(x, y)/(pi/2)
		# angle = angle if angle <= 1.0 else 1.0
		# angle = angle if angle >= -1.0 else -1.0

		print('raw',x,y)
		# print('mag angle:', mag, angle)
		self.command(x, y, 200)
		# self.command(mag, angle, 200)

	def command(self, vel, rot, scale=1.0):
		"""
		vel: 0-1
		rot: 0-2pi
		scale: scalar multiplied to velocity
		"""
		# vel *= scale
		# rot *= 200
		rot = -rot
		print('cmd:', vel, rot)
		level = 0.1

		if -level < rot < level:  # a little more than a degree
			print('straight')
			self.bot.drive_straight(vel*scale)
		elif -level < vel < level:
			print('rotation')
			sgn = -1 if rot < 0 else 1
			self.bot.drive_rotate(abs(rot*scale), sgn)
		else:
			print('turn')
			if rot >= 0:
				rot = 1.0 - rot
			else:
				rot = rot + 1.0
			# rot = abs(rot)
			# rot = 1.0 - rot

			radius = -rot*scale*2.5
			# if radius >= 0:
			# 	radius -= 2000
			# else:
			# 	radius += 2000
			vel *= scale
			self.bot.drive_turn(vel, radius)
