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


class AutoMode(object):
	def __init__(self, bot):
		self.bot = bot
		self.cliff_move = [-45, -90, 90, 45]
		self.ir_move = [-30, -60, -90, 90, 60, 30]

	def get_sensor_array(self, sensors, packets):
		sen = [0]*len(packets)
		for i, s in enumerate(packets):
			sen[i] = sensors[s]
		return sen

	def go(self, all_sensors):
		# # grab camera image
		# if self.camera:
		# 	ok, img = self.camera.read()
		#
		# 	if ok:  # good image capture
		# 		self.processImage(img)
		# 	else:
		# 		print('<<< bad image >>>')

		speed = 200

		sensors = all_sensors['create']

		# emergency stop -----------------------------------------------------
		# you really only need to do this in Full Mode
		# this is done for you in Safe Mode
		wheel_drops = (sensors.bumps_wheeldrops.wheeldrop_left, sensors.bumps_wheeldrops.wheeldrop_right)
		# handle wheel drops
		for danger in wheel_drops:
			if danger:
				print('crap ... lost the floor!!!')
				self.bot.drive_stop()
				# self.bot.drive_direct(-speed, -speed)
				# time.sleep(2)
				# self.bot.turn(180, speed)
				return

		# setup reponses ----------------------------------------------------
		ir = self.get_sensor_array(sensors, [36, 37, 38, 39, 40, 41])
		cliff = self.get_sensor_array(sensors, [20, 21, 22, 23])

		# -------------------------------------------------------------------
		# handle ir
		for s, a in zip(ir, self.ir_move):
			if s > 1000:
				self.bot.drive_direct(-speed, -speed)
				time.sleep(1)
				self.bot.turn_angle(a, speed)
				return

		# handle cliffs - really dark tape on ground to simulate obsticles
		for s, a in zip(cliff, self.cliff_move):
			if s < 1700:
				self.bot.drive_direct(-speed, -speed)
				time.sleep(1)
				self.bot.turn_angle(a, speed)
				return

		# so no issues ... drive straight
		self.bot.drive_direct(speed, speed)
		return
