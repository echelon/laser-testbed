#!/usr/bin/env python

import os
import math
import random
import cv2
import itertools
import sys
import time
import thread

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.shape import Shape

"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

"""
Globals
"""

objs = []
obj = None
ps = None
frame = None # OpenCV camera

"""
Animation code / logic
"""

class Contour(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0, ctour=None):
		super(Contour, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.ctour = [] # XXX: SET BY THREAD !!
		if ctour:
			self.ctour = ctour

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		for c in self.ctour:
			yield (c['x'], c['y'], CMAX, CMAX, CMAX)

		self.drawn = True

def camera_thread():
	"""
	This thread *has* to exist on its own or the
	camera frames will get bogged down by any
	processing that occurs on them. This will result
	in seconds-long delay and is annoying as heck.

	It's unfortunate that this must be a thread,
	but it must.
	"""
	global frame

	vc = cv2.VideoCapture(0)

	while True:
		rval, frame = vc.read()
		time.sleep(0.05)

def opencv_thread():
	global obj
	global ps
	global frame

	width = 400
	height = 400
	x1 = 150
	y1 = 70
	x2 = x1 + width
	y2 = y1 + height

	while True:

		cropped = frame[y1:y2, x1:x2]

		time.sleep(0.01)

		gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)

		time.sleep(0.01)

		kern = 9
		smooth = gray
		smooth = cv2.GaussianBlur(gray, (kern, kern), 0)

		time.sleep(0.01)

		thresh1 = 40.0 # HI -- 50 is great!
		thresh2 = thresh1 #- 15.0 # LOW -- 10 is good.
		canny = cv2.Canny(smooth, thresh1, thresh2)

		time.sleep(0.01)

		im = canny.copy()

		time.sleep(0.01)
		method = cv2.CHAIN_APPROX_NONE
		#method = cv2.CHAIN_APPROX_SIMPLE
		ctours, hier = cv2.findContours(im,
							method=method,
							mode=cv2.RETR_EXTERNAL)

		time.sleep(0.01)

		ctourObjs = []
		ctours2 = []
		i = 0
		time.sleep(0.1)
		for c in ctours:
			if len(c) < 50:
				continue

			if random.randint(0, 3) == 0:
				continue

			ct = []
			i = 0
			for d in c:
				ln = len(d)
				for e in d:
					i += 1
					# XXX: Use this to control flicker
					# by reducing the number of points
					if ln < 250 and i % 2 != 0:
						continue
					"""
					elif ln > 250 and i % 10 != 0:
						continue
					"""
					x = e[0] * -80
					y = e[1] * -80
					ct.append({'x': x, 'y': y})

			cto = Contour(ctour=ct)
			ctourObjs.append(cto)

		ps.objects = []
		ps.objects = ctourObjs

		time.sleep(0.1)

def dac_thread():
	global obj
	global ps

	d = dac.DAC(dac.find_first_dac())

	while True:
		try:
			d.play_stream(ps)

		except KeyboardInterrupt:
			sys.exit()

		except Exception as e:
			# Reset playback so galvos keep spinning
			d.last_status.playback_state = 0
			d.last_status.fullness = 1799

#
# Start Threads
#

def main():
	global obj
	global ps

	ps = PointStream()
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 7
	ps.trackingSamplePts = 7

	thread.start_new_thread(dac_thread, ())
	time.sleep(0.50)
	thread.start_new_thread(camera_thread, ())
	time.sleep(0.50)
	thread.start_new_thread(opencv_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()
