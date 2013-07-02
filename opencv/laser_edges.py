#!/usr/bin/env python

"""
Lase with OpenCV Contours.
This code was overhauled beginning May 31, 2013.

To anyone unfamiliar with Python, 'multiprocessing' and 'threading'
are two entirely different concepts in the language. Due to the
Global Interpreter Lock, 'threading' isn't actually real threading.
The 'multiprocessing' module was created to bypass the GIL. In this
script, I utilize both threading and multiprocessing. You'll need to
read the Python docs to see how this works.
"""

import os
import cv2
import sys
import math
import time
import random
import thread
import itertools
from multiprocessing import Process, Queue

from lib import dac
from lib.common import *
from lib.shape import Shape
from lib.stream import PointStream

"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

# Contour scaling
SCALE = -100
X_OFF = 0
Y_OFF = 0

"""
Globals
"""

ps = None
frame = None # OpenCV camera
queue = Queue(maxsize=1) # Multiprocess queue
#queue = Queue()

camera = cv2.VideoCapture(0)
cv2.namedWindow('window')
cv2.createTrackbar('threshLo', 'window', 40, 130, lambda x: None)
cv2.createTrackbar('threshHi', 'window', 60, 130, lambda x: None)
cv2.createTrackbar('removeUnder', 'window', 10, 50, lambda x: None)

def show_image(image, window='window'):
	cv2.imshow(window, image)
	key = cv2.waitKey(20)
	if key == 27: # exit on ESC
		sys.exit()

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
	global queue

	width = 250 # 400
	height = 250 # 400
	x1 = 150
	y1 = 70
	x2 = x1 + width
	y2 = y1 + height

	while True:
		rval, frame = camera.read()

		#time.sleep(0.01)

		cropped = frame[y1:y2, x1:x2]

		#time.sleep(0.02)

		gray = cv2.cvtColor(cropped, cv2.COLOR_RGB2GRAY)

		#time.sleep(0.02)

		kern = 9
		smooth = cv2.GaussianBlur(gray, (kern, kern), 0)

		#time.sleep(0.02)

		threshLo = cv2.getTrackbarPos('threshLo', 'window')
		threshHi = cv2.getTrackbarPos('threshHi', 'window')
		removeUnder = cv2.getTrackbarPos('removeUnder', 'window')
		canny = cv2.Canny(smooth, threshLo, threshHi)

		#time.sleep(0.02)

		im = canny.copy()

		#time.sleep(0.02)

		#method = cv2.CHAIN_APPROX_NONE
		method = cv2.CHAIN_APPROX_SIMPLE
		#mode = cv2.RETR_EXTERNAL
		#mode = cv2.RETR_TREE
		mode = cv2.RETR_LIST
		ctours, hier = cv2.findContours(im, method=method, mode=mode)

		outCtours = []
		contourImg = gray.copy() # TODO: Make Global, create just once
		contourImg.fill(0)
		for i in range(len(ctours)):
			if len(ctours[i]) < removeUnder:
				continue
			cv2.drawContours(contourImg, ctours, i, (255, 0, 0))
			outCtours.append(ctours[i])

		try:
			queue.put(outCtours, block=False)
		except:
			pass

		show_image(contourImg)

		#time.sleep(0.1)

def copy_struct_thread():
	global ps
	global queue

	while True:
		objects = []

		cv_contours = queue.get()
		#while not queue.empty():
		#	cv_contours = queue.get()

		j = 0
		for ctour in cv_contours:
			points = []
			ln = len(ctour)
			i = 0
			for x in ctour:
				pt = x[0]
				# XXX: Use this to control flicker
				# by reducing the number of points
				i += 1
				if i % 2:
					continue
				x = pt[0] * SCALE + X_OFF
				y = pt[1] * SCALE + Y_OFF
				points.append({'x': x, 'y': y})

			obj = Contour(ctour=points)
			obj.drawEveryHeuristic = True
			obj.drawEvery = 2
			obj.drawEveryCount = j % obj.drawEvery
			objects.append(obj)

		ps.setNextFrame(objects)
		time.sleep(0.2)

def dac_thread():
	global ps

	d = dac.DAC(dac.find_first_dac())

	while True:
		try:
			d.play_stream(ps)
		except KeyboardInterrupt:
			sys.exit()
		except Exception as e:
			print 'exception', e
			# Reset playback so galvos keep spinning
			d.last_status.playback_state = 0
			d.last_status.fullness = 1799

def dac_process():
	global ps

	ps = PointStream()
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 7
	ps.trackingSamplePts = 7

	thread.start_new_thread(dac_thread, ())
	time.sleep(0.50)
	thread.start_new_thread(copy_struct_thread, ())

	while True:
		time.sleep(100000)

def main():
	p = Process(target=dac_process)
	p.start()

	time.sleep(0.50)
	#thread.start_new_thread(camera_thread, ())
	#time.sleep(0.50)
	thread.start_new_thread(opencv_thread, ())

	try:
		while True:
			time.sleep(100000)
	except KeyboardInterrupt:
		print "Keyboard Interrupt"
		p.terminate()
		cv2.destroyAllWindows()
		sys.exit()

if __name__ == '__main__':
	main()
