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


class Bag(object):
	def __init__(self, filename='robot.dat'):
		files = os.listdir('./')
		for f in files:
			if f == filename:
				os.remove(filename)
		self.db = shelve.open(filename)
		self.images = []
		self.create = []
		self.imu = []
		self.time = []

	def __del__(self):
		self.db['images'] = self.images
		self.db['create'] = self.create
		self.db['imu'] = self.imu
		self.db['timestamp'] = self.time
		self.db.close()

	def push(self, image, create, imu):
		# grab timestamp
		self.time.append(time.time())

		# if image:
		jpg = cv2.imencode('.png', image)[1].tostring()  # no bennefit with doing string (1.9MB)
		self.images.append(jpg)

		# if create:
		self.create.append(create)

		# if imu:
		self.imu.append(imu)


def read(filename):
	db = shelve.open(filename)
	imgs = db['images']
	create = db['create']
	imu = db['imu']
	

	for i in range(len(imgs)):
		d = data[i]
		print(i, d)
		img = imgs[i]
		img = np.fromstring(img, np.uint8)
		frame = cv2.imdecode(img, 1)
		print('frame[{}] {}'.format(i, frame.shape))
		cv2.imshow('camera', frame)
		cv2.waitKey(300)

	print('bye ...')
	cv2.destroyAllWindows()
	db.close()


def write():
	# os.remove(filename)
	bag = Bag()
	cap = cv2.VideoCapture(0)
	imu = IMU()
	bot = pycreate2.Create2('/dev/ttyUSB0')
	bot.start()
	bot.safe()

	for i in range(100):
		# grab IMU
		a, m, g = imu.get()

		# grab create sensors
		s = bot.inputCommands()

		# grab images
		ret, frame = cap.read()
		if not ret:
			frame = None

		bag.push(image=frame, imu=(a, m, g), create=s)

		time.sleep(0.03)

	cap.release()


if __name__ == "__main__":
	write()
	# time.sleep(2)
	# read()
