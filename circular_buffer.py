#!/usr/bin/env python


class CircularBuffer(object):
	def __init__(self, size):
		"""initialization"""
		self.index = 0
		self.size = size
		self._data = []

	def push(self, value):
		"""append an element"""
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
		return(self._data)


if __name__ == "__main__":
	cb = CircularBuffer(10)

	for i in range(20):
		cb.push(i)

	print(cb.get_all())
	print('get cb[7]', cb[7])
