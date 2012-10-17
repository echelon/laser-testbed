#!/usr/bin/env python

import os
import math
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

		self.ctour = [] # XXX: SET BY THREAD
		if ctour:
			self.ctour = ctour

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		for c in self.ctour:
			x = c['x']
			y = c['y']
			yield (x, y, CMAX, CMAX, CMAX)

		self.drawn = True

class Contours(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0):
		super(Contours, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.ctours = [] # XXX: SET BY THREAD

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		"""
		rval, frame = self.vc.read()

		gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
		smooth = cv2.GaussianBlur(gray, (7,7), 0)

		binary = cv2.adaptiveThreshold(smooth, 255,
					cv2.ADAPTIVE_THRESH_MEAN_C,
					cv2.THRESH_BINARY, 3, 0)

		kern = cv2.getStructuringElement(
					cv2.MORPH_CROSS, (3,3))
		erode = cv2.erode(binary, kern)

		im = erode.copy()
		ctours, hier = cv2.findContours(im,
							method=cv2.CHAIN_APPROX_NONE,
							mode=cv2.RETR_EXTERNAL)
		"""

		"""
		for c in self.ctours:
			for d in c:
				for e in d:
					x = e[0] * 10
					y = e[1] * 10
					yield (x, y, CMAX, CMAX, CMAX)
		"""

		for c in self.ctours:
			x = c['x']
			y = c['y']
			yield (x, y, CMAX, CMAX, CMAX)


		self.drawn = True

def camera_thread():
	global frame

	vc = cv2.VideoCapture(0)

	while True:
		rval, frame = vc.read()
		time.sleep(0.1)

def opencv_thread():
	global obj
	global ps
	global frame

	#vc = cv2.VideoCapture(0)

	while True:

		#rval, frame = vc.read()
		gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)

		time.sleep(0.15)
		smooth = gray
		smooth = cv2.GaussianBlur(gray, (15,15), 0)
		#smooth = cv2.GaussianBlur(smooth, (15,15), 0)

		time.sleep(0.15)
		binary = cv2.adaptiveThreshold(smooth, 255,
					cv2.ADAPTIVE_THRESH_MEAN_C,
					cv2.THRESH_BINARY, 5, 0)

		# morph_erode, morph_...
		#kern = cv2.getStructuringElement(cv2.MORPH_CROSS, (3,3))
		kern = cv2.getStructuringElement(cv2.MORPH_CROSS, (5,5))
		time.sleep(0.15)
		erode = cv2.erode(binary, kern)
		time.sleep(0.15)
		dilate = cv2.dilate(binary, kern)
		time.sleep(0.15)
		morph = cv2.dilate(erode, kern)


		time.sleep(0.15)

		im = morph.copy()

		ctours, hier = cv2.findContours(im,
							method=cv2.CHAIN_APPROX_NONE,
							mode=cv2.RETR_EXTERNAL)


		"""
		rval, frame = vc.read()

		gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
		smooth = cv2.GaussianBlur(gray, (15,15), 0)

		time.sleep(0.05)

		binary = cv2.adaptiveThreshold(smooth, 255,
					cv2.ADAPTIVE_THRESH_MEAN_C,
					cv2.THRESH_BINARY, 7, 0)

		time.sleep(0.05)

		kern = cv2.getStructuringElement(
					cv2.MORPH_CROSS, (3,3))
		erode = cv2.erode(binary, kern)

		time.sleep(0.05)

		im = erode.copy()
		ctours, hier = cv2.findContours(im,
							method=cv2.CHAIN_APPROX_NONE,
							mode=cv2.RETR_EXTERNAL)

		"""

		time.sleep(0.15)

		ctourObjs = []
		ctours2 = []
		i = 0
		for c in ctours:
			if len(c) < 170:
				continue

			time.sleep(0.15)
			ct = []
			i = 0
			for d in c:
				for e in d:
					i += 1
					if i % 4 != 0:
						continue
					x = e[0] * -30
					y = e[1] * -30
					ct.append({'x': x, 'y': y})

			cto = Contour(ctour=ct)
			ctourObjs.append(cto)

		ps.objects = []
		ps.objects = ctourObjs

		"""
		ctourObjs = []
		for c in ctours2:
			c = Contour(ctour=c)
			ctourObjs.append(c)

		ps.objects = []
		ps.objects = ctourObjs
		"""

		time.sleep(0.1)

def dac_thread():
	global obj
	global ps

	#ps.objects.append(obj)

	while True:
		try:
			d = dac.DAC(dac.find_first_dac())
			d.play_stream(ps)

		except KeyboardInterrupt:
			sys.exit()

		except Exception as e:
			import sys, traceback
			print '\n---------------------'
			print 'Exception: %s' % e
			print '- - - - - - - - - - -'
			traceback.print_tb(sys.exc_info()[2])
			print "\n"

#
# Start Threads
#

def main():
	global obj
	global ps

	obj = Contours()
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
