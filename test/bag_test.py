#!/usr/bin/env python

from __future__ import print_function, division
import sys
sys.path.insert(0, '../lib')
from bagit import Bag
import cv2
import time


def test():
	bag = Bag('./test.json', ['imu', 'camera'])
	# bag = Bag('test.json')
	cap = cv2.VideoCapture(0)
	time.sleep(0.1)

	for i in range(2):
		ret, frame = cap.read()
		# np.random.randint(0, 255, size=(5,5))
		if ret:
			bag.push('camera', frame, True)
		else:
			print('bad image')
			# pass
		bag.push('imu', (1, 2, 3))
		print(i)
	cap.release()

	bag.close()

	# cv2.namedWindow('window', cv2.WINDOW_NORMAL)
	# db = bag.read()

	# img, dt = db['camera'][0]
	# cv2.imwrite('test.jpg', img)

	# for img, dt in db['camera']:
	# 	# print(img)
	# 	print(img.shape)
	# 	cv2.imshow('window', img)
	# 	cv2.waitKey(0) & 0xFF
	#
	# cv2.destroyAllWindows()
	# print('size:', bag.size(), 'kb')


# def create():
# 	bag = Bag('test.dat', ['imu', 'create'])
# 	# cap = cv2.VideoCapture(0)
# 	imu = IMU()
# 	bot = pycreate2.Create2('/dev/ttyUSB0')
# 	bot.start()
# 	bot.safe()
#
# 	for i in range(2):
# 		# grab IMU
# 		a, m, g = imu.get()
# 		bag.push('imu', (a, m, g))
#
# 		# grab create sensors
# 		s = bot.inputCommands()
# 		bag.push('create', s)
#
# 		# grab images
# 		# ret, frame = cap.read()
# 		# if not ret:
# 		# 	frame = None
#
# 		time.sleep(0.03)
#
# 	# cap.release()
#
#
# def imu():
# 	bag = Bag('imu.dat', ['imu'])
# 	imu = IMU()
#
# 	for i in range(1000):
# 		# grab IMU
# 		if i % 100 == 0:
# 			print('step:', i)
# 		a, m, g = imu.get()
# 		bag.push('imu', (a, m, g))
# 		time.sleep(0.03)
#
# 	bag.close()
# 	print('done ...')

def camera():
	cap = cv2.VideoCapture(0)

	for i in range(10):
		ret, frame = cap.read()
		if ret:
			cv2.imshow('window', frame)
			cv2.waitKey(10) & 0xFF

	cv2.destroyAllWindows()


if __name__ == "__main__":
	# imu()
	# check_cal()
	# write()
	# time.sleep(2)
	# read()
	test()
	# camera()
