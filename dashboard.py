#!/usr/bin/env python

from __future__ import print_function, division
import shelve
from lib.circular_buffer import CircularBuffer
import random
from math import sqrt


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


def normalize(d):
	norm = 1/sqrt(d[0]**2 + d[1]**2 + d[2]**2)
	# ans = [x*norm for x in d]
	return norm


def read(filename):
	length = 30
	db = shelve.open(filename)
	imu = db['imu']
	data = {
		'accel': CircularBuffer(length),
		'mag': CircularBuffer(length),
		'gyro': CircularBuffer(length)
	}
	for d, ts in imu:
		# print(d)
		data['accel'].push(normalize(d[0]))
		data['mag'].push(normalize(d[1]))
		data['gyro'].push(normalize(d[2]))
	return data


def dummy():
	length = 40
	data = {}
	data['accel'] = CircularBuffer(length)
	data['gyros'] = CircularBuffer(length)
	data['heading'] = CircularBuffer(length)

	# fill with random data
	for k in data:
		for _ in range(60):
			data[k].push(random.randint(-10, 10))

	return data


def run():
	data = read('imu.dat')
	dashboard(data)

if __name__ == "__main__":
	run()
