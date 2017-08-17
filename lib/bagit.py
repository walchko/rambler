#!/usr/bin/env python

from __future__ import print_function, division
# import shelve
import cv2
import time
import numpy as np
import os
# import platform
from nxp_imu import IMU
import pycreate2
import simplejson as json
# import codecs
import base64


"""
encode:
img_str = cv2.imencode('.jpg', img)[1].tostring()

decode:
nparr = np.fromstring(STRING_FROM_DATABASE, np.uint8)
img = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)

unicode errors with above

jpeg = = cv2.imencode('.jpg', img)[1]
img_str = base64.b64encode(jpeg)

now to reverse:

ii = base64.b64decode(img_str)
ii = np.fromstring(ii, dtype=np.uint8)
ii = cv2.imdecode(ii, self.depth)

"""


class Bag(object):
	written = False

	def __init__(self, filename, topics):
		self.filename = filename
		# self.reset()
		self.data = {}
		for key in topics:
			self.data[key] = []
		self.data['stringified'] = []
		self.encode = '.jpg'

	def __del__(self):
		self.close()

	def decodeB64(self, b64, depth):
		"""base64 to OpenCV"""
		ii = base64.b64decode(b64)
		ii = np.fromstring(ii, dtype=np.uint8)
		img = cv2.imdecode(ii, depth)
		return img

	def encodeB64(self, img):
		"""OpenCV to base64"""
		ret, jpeg = cv2.imencode(self.encode, img)
		if not ret:
			print('<<<< error >>>>>>')
		# jpeg = img.tobytes()
		b64 = base64.b64encode(jpeg)
		return b64

	def push(self, key, data, stringify=False):
		# have to convert images (binary) to strings
		if stringify:
			print('stringified')
			data = self.encodeB64(data)
			if key not in self.data['stringified']:
				self.data['stringified'].append(key)

		if key in self.data:
			timestamp = time.time()
			self.data[key].append((data, timestamp))
			print(key)
		else:
			raise Exception('Bag::push, Invalid key: {}'.format(key))

	# def reset(self):
	# 	files = os.listdir('./')
	# 	for f in files:
	# 		if f == self.filename:
	# 			os.remove(self.filename)
	# 	self.written = False

	def close(self):
		# if not self.written:
		# json.dump(self.data, codecs.open(self.filename, 'w', encoding='utf-8'))
		with open(self.filename, 'wb') as f:
			json.dump(self.data, f)
		self.written = True

	def read(self):
		self.data = {}
		with open(self.filename, 'rb') as f:
			data = json.load(f)

		# print(data)

		for key in data['stringified']:
			tmp = []
			print(key)
			# print(data[key])
			for b64, datestamp in data[key]:
				img = self.decodeB64(b64, 1)
				tmp.append((img, datestamp))
			data[key] = tmp
		self.data = data

		return self.data

	def size(self):
		size = os.path.getsize(self.filename)//(2**10)
		print('{}: {} kb'.format(self.filename, size))


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

	cv2.namedWindow('window', cv2.WINDOW_NORMAL)
	db = bag.read()

	img, dt = db['camera'][0]
	cv2.imwrite('test.jpg', img)

	for img, dt in db['camera']:
		# print(img)
		print(img.shape)
		cv2.imshow('window', img)
		cv2.waitKey(0) & 0xFF

	cv2.destroyAllWindows()
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
