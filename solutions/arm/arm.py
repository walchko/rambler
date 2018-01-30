#!/usr/bin/env python
#
# My test arm is 004
# 18 Nov 2017

from __future__ import division
from __future__ import print_function
import serial
from math import atan2, acos, sqrt, pi, cos, sin
import time
import os
import platform
import sys


def cosine_law(a, b, c, phase=False):
	if phase:
		angle = acos((c**2 - (a**2 + b**2))/(2*a*b))
	else:
		angle = acos((c**2 - (a**2 + b**2))/(-2*a*b))

	return angle


def mag(a, b, c=0):
	return sqrt(a**2 + b**2 + c**2)


class Arm(object):
	CLAW_OPEN = 0
	CLAW_GRAB = 90
	CLAW_CLOSED = 180

	def __init__(self, port, pwm=[800, 2300]):
		self.pwm = pwm

		# calculate angle2pwm coefficients
		servo_range = [0, 180]
		self.slope = (self.pwm[1] - self.pwm[0])/(servo_range[1] - servo_range[0])
		self.intercept = self.pwm[0] - self.slope * servo_range[0]
		# speed = 9600
		speed = 115200
		self.ser = serial.Serial(port, speed)
		if not self.ser.isOpen():
			raise Exception('Arm::init() could not open', port)
		else:
			print('Arm opened {} @ {}'.format(port, speed))

	def __del__(self):
		time.sleep(3)
		self.ser.close()
		time.sleep(0.01)

	def angle2pwm(self, angle):
		"""
		angle: servo angle in radians
		return: servo pwm
		"""
		angle *= 180/pi
		pwm = self.slope * angle + self.intercept

		# if self.pwm[0] > pwm < self.pwm[1]:
		# 	print('ERROR: {} out of limits {}'.format(pwm, self.pwm))
		# 	raise Exception('PWM value out of range')
		return int(pwm)

	def send(self, angles, cmdSleep=3, speed=2500):
		"""
		Converts an array of angles to the servo board command string.
		ex: '#0 P1500 #1 P1500 #2 P1500 #3 P1500 #4 P1500 T2500\r'

		angles: array of arm angles
		"""
		# correct dh frame and servo angles
		# angles[3] += pi/2  # angles - wrist correction
		angles[3] = pi/2 - angles[3]  # points FIXME: points like this, but angles likes the other ... frame backwards?
		angles[0] += pi/2  # base correction

		tmp = [r*180/pi for r in angles]
		print('angles:', tmp)

		# cmd = '#0 P1500 #1 P1500 #2 P1500 #3 P1500 #4 P1500 T4000\r'
		cmd = []
		for channel, a in enumerate(angles):
			pwm = self.angle2pwm(a)
			if self.pwm[0] > pwm  or pwm > self.pwm[1]:
				print('ERROR: servo[{}] PWM{} out of limits {}'.format(channel, self.pwm, pwm))
				raise Exception('PWM value out of range')
			cmd.append('#{} P{}'.format(channel, pwm))
		cmd.append('T{}\r'.format(speed))
		cmd = ' '.join(cmd)

		print('[Move] ---------------------------')
		aa = [x*180/pi for x in angles]  # convert to degrees
		print('  angles: {:6.0f} {:6.0f} {:6.0f} {:6.0f}'.format(*aa[:4]))
		print('  claw: {}'.format('open' if aa[4] == 0 else 'closed'))
		print('  cmd: {}\n'.format(cmd))

		self.ser.write(cmd)
		time.sleep(1.5*speed/1000)

	def inverse(self, x, y, z, orient, claw=0):
		"""
		Calculates inverse kinematics
		given: (x,y,z) in 3D space and claw open/closed
		"""
		l1 = 5.75
		l2 = 7.375
		l3 = 3.375

		# check workspace constraints
		if z < 0:
			raise Exception('z in ground')
		elif mag(x, y, z) > (l1 + l2 + l3):
			raise Exception('out of reach {} > {}'.format(mag(x, y, z), (l1 + l2 + l3)))

		# get x-y plane azimuth
		t1 = atan2(y, x)

		# Now, most of the arm operates in the w-z frame
		w = mag(x, y)   # new frame axis
		gamma = atan2(z, w)
		r = mag(z, w)

		c = mag(w-l3*cos(orient), z-l3*sin(orient))

		t3 = cosine_law(l1, l2, c, True)

		d = cosine_law(l2, c, l1)
		e = cosine_law(c, l3, r)
		t4 = pi - d - e

		alpha = cosine_law(l1, c, l2)
		beta = cosine_law(c, r, l3)

		t2 = alpha + beta + gamma

		return [t1, t2, t3, t4, claw*pi/180]

	def calibrate(self):
		pass

	def move_arm_angles(self, angles):
		for a in angles:
			a = [pi/180*x for x in a]
			self.send(a)

	def move_arm_points(self, points):
		for pt in points:
			angles = self.inverse(*pt)
			self.send(angles)


points_lab = [
	[10.75, 0, 5.75, 0.0, Arm.CLAW_OPEN],
	[9.5, 0, 4, 0, Arm.CLAW_OPEN],
	[9.5, 0, 0, 0, Arm.CLAW_OPEN],
	[9.5, 0, 0, 0, Arm.CLAW_GRAB],
	[9.5, 0, 4, 0.0, Arm.CLAW_GRAB],
	[7, -4, 0, 0, Arm.CLAW_GRAB],
	[7, -4, 0, 0, Arm.CLAW_OPEN],
	[7, -4, 5, 0, Arm.CLAW_OPEN],
	[10.75, 0, 5.75, 0.0, Arm.CLAW_OPEN],
]

# this seems a good test
angles_lab = [
	[0, 90, 90, 0, Arm.CLAW_OPEN],
	[0, 90, 0, 0, Arm.CLAW_CLOSED],
	[0, 90, 0, -90, Arm.CLAW_OPEN],
	[0, 90, 0, 90, Arm.CLAW_CLOSED],
	[-90, 90, 135, 45, Arm.CLAW_OPEN],
	[90, 90, 90, 0, Arm.CLAW_CLOSED],
	[-90, 90, 90, 0, Arm.CLAW_OPEN],
	[90, 90, 135, 45, Arm.CLAW_CLOSED],
	[0, 90, 90, 0, Arm.CLAW_OPEN]
]

if __name__ == "__main__":
	if len(sys.argv) != 2:
		print("Error: Please use this as follows:")
		print("    ./arm.py [angle|point] or ./arm.py [a|p]")
		exit(1)

	# automatically switch between windoze and macOS
	if platform.system() == 'Darwin':
		port = '/dev/tty.usbserial-FTF7FUMR'
	else:
		port = 'COM8'
		# port = '/dev/ttyS9'

	# if not os.path.exists(port):
	# 	print('ERROR: {} does not exist'.format(port))
	# 	exit(1)

	arm = Arm(port, pwm=[700, 2400])

	_, mode = sys.argv
	if mode == 'angle' or mode == 'a':
		arm.move_arm_angles(angles_lab)
	elif mode == 'point' or mode == 'p':
		arm.move_arm_points(points_lab)

	print('Done ... ')
