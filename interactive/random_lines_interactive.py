#!/usr/bin/env python

"""

THIS IS AN EXCELLENT TOOL TO UNDERSTAND BLANKING!

PLAY WITH THE VARIABLES BELOW

I'm writing this to learn how to effectively do blanking.

Generates a random point, blanks to the next random point.
I need to be kind to the galvos...
"""

from lib import dac
from lib.common import *
from lib.controller import *

import random
import math
import itertools
import sys
import thread
import time

from dimensions import *

# Hardware params
LASER_POWER_DENOM = 1.0 # How much to divide power by
MAXPT = 32330 # Canvas boundaries 

MAX_X = X_MAX
MIN_X = X_MIN
MAX_Y = Y_MAX
MIN_Y = Y_MIN
RUN_COLOR_THREAD = False

# Demo params
PAUSE_SAMPLE_PTS = 7000 # How long to draw point
TRAVEL_SAMPLE_PTS = 7000 # How long to blank 
SHOW_TRAVEL_PATH = True # Show blanking trace

# Change the sampling rate?
CHANGE_SAMPLING = True # Change the sample speeds
CHANGE_SAMPLING_SEC = 10
CHANGE_TRAVEL_DENOM = 2
CHANGE_PAUSE_DENOM = 1.5
CHANGE_WAIT_DENOM = 2 # Alter the wait time
CHANGE_MAX = 5000 # For eye safety
CHANGE_MIN = 30 # For galvo safety
CHANGE_WAIT_MAX = 100
CHANGE_WAIT_MIN = 10 # 1

DITHER_INC_MAX = 1000
DITHER_INC_MIN = 10
CMIN_DEMO = 10000
R, G, B = (CMAX,)*3

"""
Send the galvo to random points...
"""
class BlinkPointStream(object):

	def __init__(self):
		self.called = False
		self.stream = self.produce()

		self.waitPoints = 7000
		self.travelPoints = 7000

	def produce(self):
		while True:
			x = random.randint(MIN_X, MAX_X)
			y = random.randint(MIN_Y, MAX_Y)
			for i in xrange(0, PAUSE_SAMPLE_PTS):
				yield (x, y, 0, 0, CMAX/LASER_POWER_DENOM)

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

"""
Now with "blanking"...
"""
class BlinkPointStreamWithBlanking(BlinkPointStream):

	def produce(self):
		lastX = 0
		lastY = 0
		while True:
			x = random.randint(MIN_X, MAX_X)
			y = random.randint(MIN_Y, MAX_Y)

			# Do blanking first.
			xDiff = lastX - x
			yDiff = lastY - y
			mv = self.travelPoints
			for i in xrange(0, mv):
				percent = i/float(mv)
				xb = int(lastX - xDiff*percent)
				yb = int(lastY - yDiff*percent)
				if SHOW_TRAVEL_PATH:
					yield (xb, yb, R/LASER_POWER_DENOM,
								   G/LASER_POWER_DENOM,
								   B/LASER_POWER_DENOM)
								   
				else:
					yield (xb, yb, 0, 0, 0)

			# Show the random point
			for i in xrange(0, self.waitPoints):
				yield (x, y,
						 R/LASER_POWER_DENOM,
						 G/LASER_POWER_DENOM,
						 B/LASER_POWER_DENOM)

			lastX = x
			lastY = y

class DitherColor(object):
	def __init__(self, val=CMAX, inc=1, cmin=CMIN_DEMO, cmax=CMAX):
		self.val = val
		self.direc = -1
		self.inc = inc
		self.cmin = cmin
		self.cmax = cmax
		self.incMin = DITHER_INC_MIN
		self.incMax = DITHER_INC_MAX

	def incr(self):
		"""
		Linearly increment and decrement the color intensity.
		"""
		val = self.val

		if val < 0:
			val = 0

		if self.direc <= 0:
			val -= self.inc
			if val < self.cmin:
				val = self.cmin
				self.direc = 1
				self.randomizeRate()
		else:
			val += self.inc
			if val >= self.cmax:
				val = self.cmax
				self.direc = -1
				self.randomizeRate()

		self.val = val

	def getVal(self):
		return abs(int(self.val))

	def randomizeRate(self):
		self.inc = random.randint(self.incMin, self.incMax)

OBJ = BlinkPointStreamWithBlanking()

def dac_thread():
	"""Send stuff to the laser pj"""
	while True:
		try:
			d = dac.DAC(dac.find_first_dac())
			d.play_stream(OBJ)

		except KeyboardInterrupt:
			sys.exit()

		except:
			# Hopefully the galvos aren't melting... 
			print "EXCEPTION"
			time.sleep(0.01)
			continue

def controller_thread():
	"""Manage the joysticks with PyGame"""
	global OBJ

	controller = init_controls()

	while True:
		e = controller.getEvent()

		lv = controller.getLeftVert()
		lh = controller.getLeftHori()
		rv = controller.getRightVert()
		rh = controller.getRightHori()

		lv *= -1
		lv += 1.0

		rv *= -1
		rv += 1.0

		OBJ.waitPoints = int(7000 - (7000/2 * lv) + 5)
		OBJ.travelPoints = int(7000 - (7000/2 * rv) + 5)

		if OBJ.waitPoints == 5 and OBJ.travelPoints == 5:
			OBJ.waitPoints = 10
			OBJ.travelPoints = 10

		print (lv, OBJ.waitPoints, OBJ.travelPoints)


		"""
		lastPt = OBJ.lastPoint()
		newX = lastPt['x']
		newY = lastPt['y']

		if abs(rVert) > 0.2:
			y = lastPt['y']
			y += -1 * int(rVert * SIMPLE_TRANSLATION_SPD)
			if MIN_Y < y < MAX_Y:
				newY = y

		if abs(rHori) > 0.2:
			x = lastPt['x']
			x += -1 * int(rHori * SIMPLE_TRANSLATION_SPD)
			if MIN_X < x < MAX_X:
				newX = x
		"""

		# Player rotation
		#t = math.atan2(lVert, lHori)

		# Use triggers to toggle blink
		"""
		tOff = [0.0, -1.0]
		lTrigger = True
		rTrigger = True

		if controller.getLeftTrigger() in tOff:
			lTrigger = False

		if controller.getRightTrigger() in tOff:
			rTrigger = False
		"""

		# Keep this thread from hogging CPU
		time.sleep(0.02)

"""
def color_thread():
	global R, G, B

	rr = DitherColor(inc = random.randint(50, 500), cmin=CMAX)
	gg = DitherColor(inc = random.randint(50, 500))
	bb = DitherColor(inc = random.randint(50, 500))

	while True:
		rr.incr()
		gg.incr()
		bb.incr()
		R = int(rr.getVal())
		G = int(gg.getVal())
		B = int(bb.getVal())

		time.sleep(0.001)
"""

def color_thread():
	"""While the red laser is dead..."""
	global R, G, B

	r, g, b = (0, 0, 0)

	rn = 0
	while True:
		rn = (rn + 1) % 5

		if rn == 0:
			r = CMAX
			g = CMAX
			b = CMAX

		elif rn == 1:
			r = CMAX
			g = CMAX
			b = CMAX/2

		elif rn == 2:
			r = CMAX
			g = CMAX
			b = CMAX/3

		elif rn == 3:
			r = CMAX
			g = CMAX
			b = 0

		elif rn == 4:
			r = CMAX
			g = 0
			b = CMAX


		R = r
		G = g
		B = b

		time.sleep(0.5)


thread.start_new_thread(dac_thread, ())
thread.start_new_thread(controller_thread, ())
if RUN_COLOR_THREAD:
	thread.start_new_thread(color_thread, ())

while True:
	time.sleep(200)

