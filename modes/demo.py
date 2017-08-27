# The MIT License
#
# Copyright (c) 2017 Kevin Walchko

from __future__ import print_function
from __future__ import division
import time
# import numpy as np
# from lib.js import Joystick
# from math import cos, sin, atan2, sqrt
# from lib.circular_buffer import CircularBuffer


class DemoMode(object):
	def __init__(self, bot, path=None):
		self.bot = bot
		if path:
			self.path = path
		else:
			self.path = [
				['drive', 0.5, 1, 'forward'],
				['drive', -0.5, 1, 'back'],
				['turn angle', -90, 1, 'rite'],
				['turn angle', 90, 1, 'left'],
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
				self.bot.turn_angle(vel, 100)
			elif name in ['drive']:
				self.bot.drive_distance(vel, 200)
			else:
				raise Exception('invalid movement command')

			time.sleep(dt)

		time.sleep(3)
