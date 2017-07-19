#!/usr/bin/env python

from __future__ import division, print_function
# from nxp_imu import FXAS21002, FXOS8700
# from nxp_imu.FXAS21002 import GYRO_RANGE_250DPS
from nxp_imu import I2C
from nxp_imu import IMU
from nxp_imu import AHRS
import time


def imu():
	imu = IMU()

	print("| {:20} | {:20} | {:20} |".format("Accels [g's]", " Magnet []", "Gyros [dps]"))
	print('-'*47)
	for _ in range(10):
		a, m, g = imu.get()
		# r, p, h = ahrs.getOrientation(a, m)
		print('| {:>6.2f} {:>6.2f} {:>6.2f} | {:>6.2f} {:>6.2f} {:>6.2f} |'.format(a[0], a[1], a[2], m[0], m[1], m[2]))
		time.sleep(1.0)


def ahrs():
	imu = IMU()
	ahrs = AHRS(True)

	print("| {:20} | {:20} |".format("Accels [g's]", "Orient(r,p,h) [deg]"))
	print('-'*47)
	for _ in range(10):
		a, m, g = imu.get()
		r, p, h = ahrs.getOrientation(a, m)
		print('| {:>6.2f} {:>6.2f} {:>6.2f} | {:>6.2f} {:>6.2f} {:>6.2f} |'.format(a[0], a[1], a[2], r, p, h))
		time.sleep(1.0)


if __name__ == "__main__":
	# gyro()
	# accel()
	ahrs()
	# imu()
	print('Done ...')
