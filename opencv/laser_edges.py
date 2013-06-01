#!/usr/bin/env python

"""
Lase with OpenCV Contours.
This code was overhauled beginning May 31, 2013.
"""

import os
import cv2
import sys
import math
import time
import random
import thread
import itertools

from lib import dac
from lib.common import *
from lib.shape import Shape
from lib.stream import PointStream

"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

# Contour scaling
SCALE = -80
X_OFF = 0
Y_OFF = 0

"""
Globals
"""

objs = []
obj = None
ps = None
frame = None # OpenCV camera

camera = cv2.VideoCapture(0)
cv2.namedWindow('window')
cv2.createTrackbar('threshLo', 'window', 40, 130, lambda x: None)
cv2.createTrackbar('threshHi', 'window', 60, 130, lambda x: None)

def show_image(image, window='window'):
	cv2.imshow(window, image)
	key = cv2.waitKey(20)
	if key == 27: # exit on ESC
		sys.exit()

# Contours created by OpenCV that need to be turned 
# into laser-related structures
opencv_contours = []

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
	global camera

	while True:
		rval, frame = camera.read()
		time.sleep(0.1)

def opencv_thread():
	global obj
	global ps
	global frame
	global camera
	global opencv_contours

	width = 300 # 400
	height = 300 # 400
	x1 = 150
	y1 = 70
	x2 = x1 + width
	y2 = y1 + height

	while True:

		cropped = frame[y1:y2, x1:x2]

		time.sleep(0.02)

		gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)

		time.sleep(0.02)

		kern = 9
		smooth = cv2.GaussianBlur(gray, (kern, kern), 0)

		time.sleep(0.02)

		threshLo = cv2.getTrackbarPos('threshLo', 'window')
		threshHi = cv2.getTrackbarPos('threshHi', 'window')
		canny = cv2.Canny(smooth, threshLo, threshHi)

		time.sleep(0.02)

		im = canny.copy()

		time.sleep(0.02)

		method = cv2.CHAIN_APPROX_NONE
		#method = cv2.CHAIN_APPROX_SIMPLE
		#mode = cv2.RETR_EXTERNAL
		mode = cv2.RETR_LIST
		ctours, hier = cv2.findContours(im, method=method, mode=mode)

		opencv_contours = []
		opencv_contours = ctours

		contourImg = gray.copy()
		contourImg.fill(0)
		for i in range(len(ctours)):
			cv2.drawContours(contourImg, ctours, i, (255, 0, 0))

		show_image(contourImg)

		time.sleep(0.1)

def copy_struct_thread():
	global ps
	global opencv_contours

	size = 50 # 80

	while True:
		#print "Num ctours: %d " % len(opencv_contours)
		objects = []
		for ctour in opencv_contours:
			if len(ctour) < 10:
				continue

			ct = []
			i = 0
			for d in ctour:
				ln = len(d)
				for e in d:
					i += 1
					# XXX: Use this to control flicker
					# by reducing the number of points
					"""
					if ln < 250 and i % 2 != 0:
						continue
					"""
					"""
					elif ln > 250 and i % 10 != 0:
						continue
					"""
					x = e[0] * SCALE + X_OFF
					y = e[1] * SCALE + Y_OFF
					ct.append({'x': x, 'y': y})

			cto = Contour(ctour=ct)
			objects.append(cto)

		#ps.objects = []
		ps.setNextFrame(objects)

		#print "Contour objects created: %d" % len(objects)
		#print len(ctourObjs)

		time.sleep(1.0)

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
	time.sleep(0.50)
	thread.start_new_thread(copy_struct_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()
