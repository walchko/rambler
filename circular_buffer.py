#!/usr/bin/env python

from __future__ import print_function
import sparkline

class CircularBuffer(object):
	def __init__(self, size):
		"""initialization"""
		self.index = 0
		self.size = size
		self._data = []
		self.sum = 0.0
		self.min = 1E900
		self.max = -1E900

	def push(self, value):
		"""append an element"""
		self.sum += value
		self.max = value if value > self.max else self.max
		self.min = value if value < self.min else self.min
		
		if len(self._data) == self.size:
			self._data[self.index] = value
		else:
			self._data.append(value)
		self.index = (self.index + 1) % self.size

	def __getitem__(self, key):
		"""get element by index like a regular array"""
		return(self._data[key])

	def __repr__(self):
		"""return string representation"""
		return self._data.__repr__() + ' (' + str(len(self._data))+' items)'

	def get_all(self):
		"""return a list of all the elements"""
		# return(self._data)
		ret = []
		if self.index > 0:
			ret = self._data[self.index:self.size] + self._data[0:self.index]
		else:
			ret = self._data
		return ret

	def get_last(self):
		return self._data[self.index-1]


if __name__ == "__main__":
	cb = CircularBuffer(60)

	for i in range(200):
		cb.push(i)

	print(cb.get_all())
	print('get cb[7]', cb[7])
	print('get cb[0]', cb[0])
	print('get last', cb.get_last())
	print('ine', cb.get_last(), sparkline.sparkify(cb.get_all()).encode('utf-8'))
	print(cb.get_last(), sparkline.sparkify(cb.get_all()))