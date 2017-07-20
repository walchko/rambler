#!/usr/bin/env python

import shelve
import cv2
import time
import numpy as np
import os
import platform
from nxp_imu import IMU
import pycreate2


"""
encode:
img_str = cv2.imencode('.jpg', img)[1].tostring()

decode:
nparr = np.fromstring(STRING_FROM_DATABASE, np.uint8)
img = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
"""

filename = 'robot.dat'


class Bag(object):
	def __init__(self, filename, topics):
		files = os.listdir('./')
		for f in files:
			if f == filename:
				os.remove(filename)
		self.db = shelve.open(filename)
		self.data = {}
		for key in topics:
			self.data[key] = []

	def __del__(self):
		for k, v in self.data.items():
			self.db[k] = v
		time.sleep(0.5)
		self.db.close()

	def push(self, key, data, stringify=False):
		# have to convert images (binary) to strings
		# if stringify:
		# 	data = cv2.imencode('.png', data)[1].tostring()  # no bennefit with doing string (1.9MB)

		if key in self.data:
			timestamp = time.time()
			self.data[key].append([data, timestamp])
		else:
			raise Exception('Bag::push, Invalid key: {}'.format(key))

# def read(filename):
# 	db = shelve.open(filename)
# 	imgs = db['images']
# 	create = db['create']
# 	imu = db['imu']
#
#
# 	for i in range(len(imgs)):
# 		d = data[i]
# 		print(i, d)
# 		img = imgs[i]
# 		img = np.fromstring(img, np.uint8)
# 		frame = cv2.imdecode(img, 1)
# 		print('frame[{}] {}'.format(i, frame.shape))
# 		cv2.imshow('camera', frame)
# 		cv2.waitKey(300)
#
# 	print('bye ...')
# 	cv2.destroyAllWindows()
# 	db.close()


def write():
	bag = Bag(filename, ['imu', 'create'])
	# cap = cv2.VideoCapture(0)
	imu = IMU()
	bot = pycreate2.Create2('/dev/ttyUSB0')
	bot.start()
	bot.safe()

	for i in range(100):
		# grab IMU
		a, m, g = imu.get()
		bag.push('imu', (a, m, g))

		# grab create sensors
		s = bot.inputCommands()
		bag.push('create', s)

		# grab images
		# ret, frame = cap.read()
		# if not ret:
		# 	frame = None

		time.sleep(0.03)

	# cap.release()


if __name__ == "__main__":
	write()
	# time.sleep(2)
	# read()
