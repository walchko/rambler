#!/usr/bin/env python

from __future__ import division
from __future__ import print_function
import serial
from math import atan2, acos, sqrt, pi, cos, sin
import time

def cosine_law(a, b, c, phase=False):
	if phase:
		angle = acos((c**2 - (a**2 + b**2))/(2*a*b))
	else:
		angle = acos((c**2 - (a**2 + b**2))/(-2*a*b))

	# if 1 < angle > -1:
	# 	raise Exception('angle outside range', angle)
	return angle


def line(x1, y1, x2, y2):
	return sqrt((x2-x1)**2 + (y2-y1)**2)


def mag(a, b):
	return sqrt(a**2 + b**2)


def mag3(a, b, c):
	return sqrt(a**2 + b**2 + c**2)


class Arm(object):
	range = [0, 180]   # x
	# pwm = [900, 2100]  # y
	pwm = [700, 2300]  # y
	CLAW_OPEN = 0
	CLAW_CLOSED = 90*pi/180

	def __init__(self, port):
		self.slope = (self.pwm[1] - self.pwm[0])/(self.range[1] - self.range[0])
		self.intercept = self.pwm[0] - self.slope * self.range[0]

		self.ser = serial.Serial(port, 115200)
		if not self.ser.isOpen():
			raise Exception('Arm::init() could not open', port)
		else:
			print('Arm opened {} @ 115200'.format(port))

	def __del__(self):
		# could also move it to a neutral position
		# rest = [[90, 90, 90, 90, 90]]
		# self.set(rest)
		time.sleep(3)
		self.ser.close()
		time.sleep(0.01)

	def set(self, angles):
		# cmd = '#0 P1500 #1 P1500 #2 P1500 #3 P1500 #4 P1500 T4000\r'
		cmd = []
		for channel, a in enumerate(angles):
			a *= 180/pi
			pwm = self.slope * a + self.intercept
			cmd.append('#{} P{}'.format(channel, int(pwm)))
		cmd.append('T2000\r')
		return ' '.join(cmd)

	def inverse(self, x, y, z, orient, claw=0):
		l1 = 5.75
		l2 = 7.375
		l3 = 3.375

		# check workspace constraints
		if z < 0:
			raise Exception('z in ground')
		elif mag3(x,y,z) > (l1 + l2 + l3):
			raise Exception('out of reach {} > {}'.format(mag3(x,y,z), (l1 + l2 + l3)))

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

		return [t1, t2, t3, t4, claw]

	def run(self):
		points = [
			[10.75, 0, 5.75, 0.0, self.CLAW_OPEN],
			# [7.385, 0, 5.75-3.375, -pi/2],
			# [5, 0, 0, -pi/2],
			# [7,-3,0, -pi/2],
			# [7,6,4, -pi/2],
			[9.5, 0, 4, 0, self.CLAW_OPEN],
			[9.5, 0, 0, 0, self.CLAW_OPEN],
			[9.5, 0, 0, 0, self.CLAW_CLOSED],
			[9.5, 0, 4, 0.0, self.CLAW_CLOSED],
			[7, -4, 0, 0, self.CLAW_CLOSED],
			[7, -4, 0, 0, self.CLAW_OPEN],
			[7, -4, 5, 0, self.CLAW_OPEN],
			[10.75, 0, 5.75, 0.0, self.CLAW_OPEN],
		]

		for pt in points:
			# angles = (pi/2, pi/2, pi/2, 0)
			angles = self.inverse(*pt)
			# angles[3] += pi/2  # wrist correction
			angles[3] = pi/2 - angles[3]
			angles[0] += pi/2  # base correction
			print('[Move] ---------------------------')
			for i, a in enumerate(angles):
				print('  angle {}: {:6.1f}'.format(i, a*180/pi))
			cmd = self.set(angles)  # send to robot arm
			print('  cmd: {}'.format(cmd))
			print('')
			self.ser.write(cmd)
			time.sleep(3)


if __name__ == "__main__":
	arm = Arm('COM3')
	arm.run()

	print('Done ... ')
