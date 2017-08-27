# The MIT License
#
# Copyright (c) 2017 Kevin Walchko

from __future__ import print_function
from __future__ import division
import sys
sys.path.insert(0, '../lib')
import time
import numpy as np
from lib.js import Joystick
from math import cos, sin, atan2, sqrt
from lib.circular_buffer import CircularBuffer


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
