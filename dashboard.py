#!/usr/bin/env python

from __future__ import print_function, division
import shelve
from circular_buffer import CircularBuffer
import random
from math import sqrt
from shelve import DbfilenameShelf
from bagit import Bag


def dashboard(data):
	header = 80

	print('='*header)
	print(' {:>15} [{:>5} {:<5}] {:>5} {:>30} {:<5}'.format(
		'Sensor',
		'Max',
		'Min',
		'First',
		' ',
		'Last'
	))
	print('-'*header)
	for k in data:
		print(' {:>15} [{:5.1} {:5.1}] {:>5.1} {:20} {:>5.1}'.format(
			k,
			data[k].max,
			data[k].min,
			data[k].get_first(),
			data[k].spark(),
			data[k].get_last(),
		))
	print('-'*header)


def norm(d):
	return 1/sqrt(d[0]**2 + d[1]**2 + d[2]**2)


def read(filename):
	length = 30
	db = shelve.open(filename)
	ret = {}
	# print(db.keys())
	for key in db:
		# print(key)
		ret[key] = CircularBuffer(length)
		data = db[key]
		for d, ts in data:
		# for d in data:
			ret[key].push((d))
	return ret


def createDummyData(filename, num):
	# db = DbfilenameShelf(filename)
	keys = ['accel', 'gyros', 'mag']
	bag = Bag(filename, ['imu', 'create'])

	for _ in range(200):
		a = [random.uniform(-2,2) for x in range(3)]
		m = [random.uniform(-6,6) for x in range(3)]
		g = [random.uniform(-100,100) for x in range(3)]
		bag.push('imu', (a, m, g))
	bag.close()


def run():
	# createDummyData('dummy.dat', 200)
	# print(data)
	data = read('dummy.dat')
	dashboard(data)

if __name__ == "__main__":
	run()
