#!/usr/bin/env python

from __future__ import division, print_function
from the_collector import BagReader
import cv2


def pCamera(frame):
	cv2.imshow('camera', frame)
	cv2.waitKey(100)


def pIMU(a, m):
	print('Accel: {:6.2f} {:6.2f} {:6.2f}'.format(*a))
	print('Mag: {:6.2f} {:6.2f} {:6.2f}'.format(*m))


def read_bag(filename, compress):
	"""
	Given a file, open and display images in file.
	"""
	bag = BagReader()
	bag.use_compression = compress
	data = bag.load(filename)

	cam = data['camera']
	accel = data['accel']
	mag = data['mag']

	for c, a, m in zip(cam, accel, mag):
		pIMU(a[0], m[0])
		pCamera(c[0])


if __name__ == "__main__":
	filename = 'test2.json'
	compress = True
	read_bag(filename, compress)
