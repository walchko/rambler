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
	def __init__(self, bot, sensors):
		self.bot = bot
		self.sensors = sensors

		self.data = {
			'current':  CircularBuffer(20),
			'voltage':  CircularBuffer(20),
			'distance': CircularBuffer(20),
			'ir':       CircularBuffer(6),
			'cliff':    CircularBuffer(4)
		}

	def __del__(self):
		pass

	def go(self, all_sensors):
		sensors = all_sensors['create']
		if sensors is None:
			print('No valid sensor info')
			return

		for s in [sensors.cliff_left_signal, sensors.cliff_front_left_signal, sensors.cliff_front_right_signal, sensors.cliff_right_signal]:
			if s < 1800:
				print('<<<<<<<<<<<>>>>>>>>>>>>>>>>')
				print(' cliff: {}'.format(s))
				print('<<<<<<<<<<<>>>>>>>>>>>>>>>>')

		self.data['current'].push(sensors.current)
		self.data['voltage'].push(sensors.voltage)
		self.data['distance'].push(sensors.distance)

		for i in [36, 37, 38, 39, 40, 41]:
			self.data['ir'].push(sensors[i])

		for i in [20, 21, 22, 23]:
			self.data['cliff'].push(sensors[i])

		po = [
			'--------------------------------------------------------',
			'Light Bumper: {:6} {:6} {:6} L|R {:6} {:6} {:6}'.format(
				sensors.light_bumper_left,
				sensors.light_bumper_front_left,
				sensors.light_bumper_center_left,
				sensors.light_bumper_center_right,
				sensors.light_bumper_front_right,
				sensors.light_bumper_right
			),
			'Cliff: {:6} {:6} {:6} {:6}'.format(
				sensors.cliff_left_signal,
				sensors.cliff_front_left_signal,
				sensors.cliff_front_right_signal,
				sensors.cliff_right_signal
			),
			'Encoders [L, R]: {:7} {:7}'.format(sensors.encoder_counts_left, sensors.encoder_counts_right),
			'Distance: {:8}  Total: {:10}'.format(sensors.distance, self.data['distance'].sum),
			'--------------------------------------------------------',
			'Power: {:6} mAhr [{:3} %]'.format(sensors.battery_charge, int(100.0*sensors.battery_charge/sensors.battery_capacity)),
			'Voltage: {:7.1f} V    Current: {:7.1f} A'.format(sensors.voltage/1000, sensors.current/1000)
		]

		for s in po:
			print(s)

		header = 80
		print('='*header)
		print(' {:>15} [{:>5} {:<5}] {:>5} {:>30} {:<5}'.format(
			'Sensor',
			'Max',
			'Min',
			'First',
			' ',
			'Last'
		))
		print('-'*header)
		# for k in ['voltage', 'current', 'ir']:
		for k in self.data.keys():
			print(' {:>15} [{:5.1f} {:5.1f}] {:>5.1f} {:20} {:>5.1f}'.format(
				k,
				self.data[k].max,
				self.data[k].min,
				self.data[k].get_first(),
				self.data[k].spark(),
				self.data[k].get_last(),
			))
		print('-'*header)

		time.sleep(0.1)


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
				['direct', (250, 250), 2, 'for'],
				['direct', (-250, -250), 2, 'back'],
				['direct', (250, -250), 2, 'rite'],
				['direct', (-250, 250), 2, 'left'],
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

	def go(self, all_sensors=None):
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
			elif name in ['direct']:
				r, l = vel
				self.bot.drive_direct(r, l)
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
