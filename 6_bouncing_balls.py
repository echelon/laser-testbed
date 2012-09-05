#!/usr/bin/env python

"""
Two balls bouncing off walls. 

The problems encountered here are "blanking" the laser as it moves from
one ball to the next (so there is no line drawn between them), as well as
turning on the laser in time to draw a complete circle for each ball. 
"""

from daclib import dac
from daclib.common import * 

import math
import random
import itertools
import sys

import thread
import time

LASER_POWER_DENOM = 4
SHOW_BLANKING_PATH = False
BLANK_SAMPLE_PTS = 30

class Entity(object):
	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0):
		self.x = x
		self.y = y
		self.r = r
		self.g = g
		self.b = b

		# Cached first and last points. 
		self.firstPt = 0
		self.lastPt = 0

	def produce(self):
		self.lastPt = (0, 0, 0, 0, 0)
		return self.lastPt

	def cacheFirstPt(self):
		# XXX/FIXME: This is a hack (should I be using generators?)
		for x in self.produce():
			self.firstPt = x
			break


class Ball(Entity):
	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0, radius = 1200):
		super(Ball, self).__init__(x, y, r, g, b)
		self.radius = radius
		self.drawn = False

	def produce(self):
		# REMOVED LOOP
		for i in xrange(0, 40, 1):
			i = float(i) / 40 * 2 * math.pi
			x = int(math.cos(i) * self.radius) + self.x
			y = int(math.sin(i) * self.radius) + self.y

			self.lastPt = (x, y, self.r, self.g, self.b)
			yield self.lastPt

		self.drawn = True

class PointStream(object):
	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def produce(self):
		"""
		This infinite loop functions as an infinite point generator.
		It generates points for both balls as well as the "blanking"
		that must occur between them.

		I am still not very comfortable with this 'inversion of 
		control' that the DAC lib expects, but I am getting used to 
		it. 
		"""
		while True: 

			# Generate first points of the objects.
			b1.cacheFirstPt()
			b2.cacheFirstPt()

			if not b1.drawn:
				yield b1.firstPt
				for x in b1.produce():
					yield x

			# Paint last pt for smoothness
			for x in xrange(BLANK_SAMPLE_PTS/4):
				yield b1.firstPt

			# Paint empty for smoothness
			for x in xrange(BLANK_SAMPLE_PTS):
				yield (b1.lastPt[0], b1.lastPt[1], 0, 0, 0)

			# Blanking... 
			lastX = b1.lastPt[0]
			lastY = b1.lastPt[1]
			xDiff = b1.lastPt[0] - b2.firstPt[0]
			yDiff = b1.lastPt[1] - b2.firstPt[1]
			mv = BLANK_SAMPLE_PTS
			for i in xrange(0, mv): 
				percent = i/float(mv)
				xb = int(lastX - xDiff*percent)
				yb = int(lastY - yDiff*percent)
				#print "Blank at: %d, %d" % (xb, yb)
				if SHOW_BLANKING_PATH:
					# XXX: "See" the blanking
					yield (xb, yb, CMAX/LASER_POWER_DENOM,
								   CMAX/LASER_POWER_DENOM,
								   CMAX/LASER_POWER_DENOM)
				else:
					yield (xb, yb, 0, 0, 0)

			if not b2.drawn:
				yield b2.firstPt
				for x in b2.produce():
					yield x

			b1.drawn = False
			b2.drawn = False

			# Paint last pt for smoothness
			for x in xrange(BLANK_SAMPLE_PTS/4):
				yield b2.firstPt

			# Paint empty for smoothness
			for x in xrange(BLANK_SAMPLE_PTS):
				yield (b2.lastPt[0], b2.lastPt[1], 0, 0, 0)

			# Blanking... 
			lastX = b2.lastPt[0]
			lastY = b2.lastPt[1]
			xDiff = b2.lastPt[0] - b1.firstPt[0]
			yDiff = b2.lastPt[1] - b1.firstPt[1]
			mv = BLANK_SAMPLE_PTS
			for i in xrange(0, mv): 
				percent = i/float(mv)
				xb = int(lastX - xDiff*percent)
				yb = int(lastY - yDiff*percent)
				#print "Blank at: %d, %d" % (xb, yb)
				if SHOW_BLANKING_PATH:
					# XXX: "See" the blanking
					yield (xb, yb, CMAX/LASER_POWER_DENOM,
								   CMAX/LASER_POWER_DENOM,
								   CMAX/LASER_POWER_DENOM)
				else:
					yield (xb, yb, 0, 0, 0)



							
	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

"""
Main Program
"""

b1 = Ball(0, 0, 0, 0, CMAX/3, 3000)
b2 = Ball(0, 0, 0, CMAX/2, 0, 8000)
ps = PointStream()

def dac_thread():
	while True:
		try:
			d = dac.DAC(dac.find_first_dac())
			d.play_stream(ps)
		except Exception as e:
			print e
			pass

def move_thread():
	"""
	This thread increments the ball positions and randomizes ball 
	velocities when they "bounce" off the walls. 
	This is just so sloppy of me... don't judge.
	"""
	MAX_X = 20000
	MIN_X = -20000
	MAX_Y = 20000
	MIN_Y = -20000

	xDirec1 = 0
	yDirec1 = 0
	xAdd1 = 500
	yAdd1 = 500

	xDirec2 = 0
	yDirec2 = 0
	xAdd2 = 500
	yAdd2 = 500

	while True:
		if b1.x > MAX_X:
			xDirec1 = 0
			xAdd1 = random.randint(100, 1000)
		elif b1.x < MIN_X:
			xDirec1 = 1
			xAdd1 = random.randint(100, 1000)
		if b1.y > MAX_Y:
			yDirec1 = 0
			yAdd1 = random.randint(100, 1000)
		elif b1.y < MIN_Y:
			yDirec1 = 1
			yAdd1 = random.randint(100, 1000)

		if xDirec1:
			b1.x += xAdd1
		else:
			b1.x -= xAdd1

		if yDirec1:
			b1.y += yAdd1
		else:
			b1.y -= yAdd1

		if b2.x > MAX_X:
			xDirec2 = 0
			xAdd2 = random.randint(100, 1000)
		elif b2.x < MIN_X:
			xDirec2 = 1
			xAdd2 = random.randint(100, 1000)
		if b2.y > MAX_Y:
			yDirec2 = 0
			yAdd2 = random.randint(100, 1000)
		elif b2.y < MIN_Y:
			yDirec2 = 1
			yAdd2 = random.randint(100, 1000)

		if xDirec2:
			b2.x += xAdd2
		else:
			b2.x -= xAdd2

		if yDirec2:
			b2.y += yAdd2
		else:
			b2.y -= yAdd2

		time.sleep(0.020)


thread.start_new_thread(dac_thread, ())
thread.start_new_thread(move_thread, ())

while True:
	time.sleep(2)


