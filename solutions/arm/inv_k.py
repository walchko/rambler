#!/usr/bin/env python

from __future__ import division
from __future__ import print_function
from math import atan2, acos, sqrt, pi


def cosine_law(a, b, c, phase=False):
	if phase:
		angle = acos((c**2 - (a**2 + b**2))/(2*a*b))
	else:
		angle = acos((c**2 - (a**2 + b**2))/(-2*a*b))

	if 1 < angle > -1:
		raise Exception('angle outside range')
	return angle


def line(x1, y1, x2, y2):
	return sqrt((x2-x1)**2 + (y2-y1)**2)


def mag(a, b):
	return sqrt(a**2 + b**2)


def mag3(a, b, c):
	return sqrt(a**2 + b**2 + c**2)


def inverse(x, y, z):
	l1 = 5.75
	l2 = 7.375
	l3 = 3.375

	# check workspace constraints
	if z < 0:
		raise Exception('z in ground')
	elif mag3(x,y,z) > (l1 + l2 + l3):
		raise Exception('out of reach')

	# get x-y plane azimuth
	t1 = atan2(y, x)

	# Now, most of the arm operates in the w-z frame
	w = mag(x, y)         # new frame axis
	gamma = atan2(z, w)
	r = mag(z, w)

	c = mag(w-l3*cos(orient), z-l3*sin(orient))

	t3 = cosine_law(l1, l2, c, True)

	d = cosine_law(l2, c, l1)
	e = cosine_law(c, l3, r)
	t4 = pi - d - e

	alpha = cosine_law(l1, c, l2)
	beta = cosine_law(c,r,l3)

	t2 = alpha + beta + gamma

	return (t1, t2, t3, t4)


if __name__ == '__main__':
	angles = inverse(5, 5, 5)
	print(angles)
