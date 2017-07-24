#!/usr/bin/env python

from shelve import DbfilenameShelf as DataBase
from whichdb import whichdb


def write():
	db = DataBase('not_bsd.dat')
	db['a'] = range(1000)
	db['b'] = range(2000)
	db.close()


def read():
	db = DataBase('not_bsd.dat')
	a = db['a']
	b = db['b']
	db.close()

	print('a', a)
	print('b', b)


if __name__ == "__main__":
	# read()
	for filename in ['not_bsd.dat', 'imu.dat', 'robot.dat']:
		print(filename, whichdb(filename))
