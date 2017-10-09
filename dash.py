#!/usr/bin/env python

from __future__ import division, print_function
from the_collector.bagit import BagReader
import cv2
# import time


def pCamera(frame):
	cv2.imshow('camera', frame)
	cv2.waitKey(100)


def pIMU(a, m):
	print('Accel: {:6.2f} {:6.2f} {:6.2f}'.format(*a))
	print('Mag: {:6.2f} {:6.2f} {:6.2f}'.format(*m))


def pCreate(cr):
	print('')


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

	_, start = accel[0]

	for i, pt in enumerate(cam):
		img, ts = pt
		print('Time: {}'.format(ts - start))
		pCamera(img)
		pIMU(accel[i][0], mag[i][0])


if __name__ == "__main__":
	filename = 'test2.json'
	compress = True
	read_bag(filename, compress)
