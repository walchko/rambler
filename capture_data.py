#!/usr/bin/env python
# The MIT License
#
# Copyright (c) 2017 Kevin Walchko

from __future__ import print_function
from __future__ import division
import platform
import time
import sparkline

# pycreate ----------------
import pycreate2

# library -----------------
from the_collector.bagit import BagWriter

# navigation and sensors --
from ins_nav import AHRS
from ins_nav.utils import quat2euler
from opencvutils import Camera
from nxp_imu import IMU


def main():
	port = '/dev/ttyUSB0'
	bot = bot = pycreate2.Create2(port)
	bot.start()
	bot.safe()
	bot.drive_stop()

	image_size = (320, 240)
	camera = Camera(cam='pi')
	camera.init(win=image_size)

	imu = IMU()

	bag = BagWriter()
	bag.open(['camera', 'accel', 'mag', 'cr'])
	bag.stringify('camera')
	bag.use_compression = True

	try:
		for i in range(100):
			ret, frame = camera.read()
			if ret:
				bag.push('camera', frame)
			else:
				print('>> bad frame', i)

			sen = bot.get_sensors()
			bag.push('cr', sen)

			a, m, g = imu.get()
			bag.push('accel', a)
			bag.push('mag', m)

			# time.sleep(0.025)

			print(i)

	except KeyboardInterrupt:
		print(' ctrl-c pressed, bye ...')

	except Exception as e:
		print('')
		print('Something else happened ... :(')
		print('Maybe the robot is not on ... press the start button')
		print('-'*30)
		print(e)

	bag.write('test.json')


if __name__ == '__main__':
	main()
