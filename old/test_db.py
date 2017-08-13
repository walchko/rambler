#!/usr/bin/env python

from __future__ import print_function, division
from shelve import DbfilenameShelf as DataBase
from whichdb import whichdb
import dumbdbm
import shelve


def write():
	# db = DataBase('not_bsd.dat')
	dumb = dumbdbm.open('test_dumb.dat')
	db = shelve.Shelf(dumb)
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
	write()
	# for filename in ['not_bsd.dat', 'imu.dat', 'robot.dat']:
	# 	print(filename, whichdb(filename))
	print('test_dumb.dat', whichdb('test_dumb.dat'))
