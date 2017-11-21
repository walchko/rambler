#!/usr/bin/env python
from __future__ import division
from __future__ import print_function
import serial
from math import pi
import time
import sys


def run(ser, servo, angle):
	# cmd = '#0 P1500 #1 P1500 #2 P1500 #3 P1500 #4 P1500 T4000\r'
	# [500, 2200] - 0
	# [700, 2300] - 1-4
	pwm = [700, 2400]       # change me
	angle_range = [0, 180]  # change me

	# check bounds
	if 0 > angle > 180:
		raise Exception('Angle out of range', angle)
	if 0 > servo > 4:
		raise Exception('Servo out of range', servo)

	# make command
	cmd = []
	intercept = pwm[0]
	slope = (pwm[1] - intercept)/angle_range[1]
	pwm = slope * angle + intercept
	pwm = int(pwm)
	cmd.append('#{} P{}'.format(servo, pwm))
	cmd.append('T3000\r')
	cmd = ' '.join(cmd)

	print('servo[{}] -> {}  cmd: {}'.format(servo, angle, cmd))
	ser.write(cmd)


if __name__ == '__main__':
	# grab command line args
	if len(sys.argv) != 3:
		print("Error: Please use this as follows:")
		print("    test [servo_num] [angle_deg]")
		exit(1)

	# port = 'COM3'
	port = '/dev/tty.usbserial-FTF7FUMR'
	ser = serial.Serial(port, 115200)
	if not ser.isOpen():
		raise Exception('Arm::init() could not open', port)

	_, servo, angle = sys.argv
	run(ser, int(servo), float(angle))
	time.sleep(1)

	# for servo in [0,1,2,3]:
	# 	for angle in [0, 45, 90, 135, 180]:
	# 		run(ser, servo, angle)
	# 		time.sleep(3)
