#!/usr/bin/env python

from __future__ import division, print_function
from the_collector.bagit import BagReader
import cv2
import time


def pCamera(frame):
	cv2.imshow('camera', frame)
	cv2.waitKey(1)


def pIMU(a, m):
	print('Accel: {:.2f}  Mag: {:.2f}'.format(a, m))


def pCreate(cr):
	print('')


def read_bag(filename, compress):
    """
    Given a file, open and display images in file.
    """
    bag = BagReader()
    bag.use_compression = compress
    data = bag.load(filename)

	


if __name__ == "__main__":
    filename = 'test.json'
    compress = True
    read_bag(filename, compress)
