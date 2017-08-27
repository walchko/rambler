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


class IdleMode(object):
	def __init__(self, bot):
		self.bot = bot

	def __del__(self):
		pass

	def go(self, all_sensors):
		time.sleep(0.2)
