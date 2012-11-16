#!/usr/bin/env python

"""
A rotating, translating, transforming (growing) square.
Integrates some code from my GameJam project, Laser Asteroids.
"""

import math
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

SQUARE_X = 0
SQUARE_Y = 0

SQUARE_R = CMAX
SQUARE_G = CMAX
SQUARE_B = CMAX

SQUARE_EDGE_SAMPLE_PTS = 50
SQUARE_VERTEX_SAMPLE_PTS = 10

"""
# School parking deck to J-building params
SQUARE_RADIUS_MIN = 5
SQUARE_RADIUS_MAX = 50
SQUARE_RADIUS_INC = 10
PAN_X_INC_MAG = 400
PAN_X_MAX = 2500
PAN_X_MIN = -2500
"""

SQUARE_RADIUS_MIN = 3000
SQUARE_RADIUS_MAX = 5200
SQUARE_RADIUS_INC = 250
PAN_X_INC_MAG = 1500
PAN_X_MAX = 25000
PAN_X_MIN = -25000

SPIN_THETA_INC = math.pi / 6

"""
CODE BEGINS HERE
"""

class Square(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0,
			radius = 8200):

		super(Square, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.radius = radius

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		# Generate points
		ed = self.radius

		pts = []
		pts.append({'x': ed, 'y': ed})
		pts.append({'x': -ed, 'y': ed})
		pts.append({'x': -ed, 'y': -ed})
		pts.append({'x': ed, 'y': -ed})

		# Rotate points
		for p in pts:
			x = p['x']
			y = p['y']
			p['x'] = x*math.cos(self.theta) \
					- y*math.sin(self.theta)
			p['y'] = y*math.cos(self.theta) \
					+ x*math.sin(self.theta)

		# Translate points
		for pt in pts:
			pt['x'] += self.x
			pt['y'] += self.y

		r = 0 if not self.r else int(self.r /
				LASER_POWER_DENOM)
		g = 0 if not self.g or LASER_POWER_DENOM > \
				4 else self.g
		b = 0 if not self.b else int(self.b /
				LASER_POWER_DENOM)

		def make_line(pt1, pt2, steps=200):
			xdiff = pt1['x'] - pt2['x']
			ydiff = pt1['y'] - pt2['y']
			line = []
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = pt1['x'] - (xdiff * j)
				y = pt1['y'] - (ydiff * j)
				# XXX: FIX COLORS
				line.append((x, y, r, g, b))
			return line

		# DRAW THE SHAPE

		p = None # Save in scope

		for p in make_line(pts[0], pts[1],
				SQUARE_EDGE_SAMPLE_PTS):
			break
		for i in range(int(round(
				SQUARE_VERTEX_SAMPLE_PTS/2.0))):
			yield p
		for p in make_line(pts[0], pts[1],
				SQUARE_EDGE_SAMPLE_PTS):
			yield p
		for i in range(SQUARE_VERTEX_SAMPLE_PTS):
			yield p
		for p in make_line(pts[1], pts[2],
				SQUARE_EDGE_SAMPLE_PTS):
			yield p
		for i in range(SQUARE_VERTEX_SAMPLE_PTS):
			yield p
		for p in make_line(pts[2], pts[3],
				SQUARE_EDGE_SAMPLE_PTS):
			yield p
		for i in range(SQUARE_VERTEX_SAMPLE_PTS):
			yield p
		for p in make_line(pts[3], pts[0],
				SQUARE_EDGE_SAMPLE_PTS):
			self.lastPt = p # KEEP BOTH
			yield p
		for i in range(int(round(
				SQUARE_VERTEX_SAMPLE_PTS/2.0))):
			self.lastPt = p # KEEP BOTH
			yield p

		self.drawn = True

def dac_thread():
	global SQUARE
	global SQUARE_X, SQUARE_Y
	global SQUARE_R, SQUARE_G, SQUARE_B
	global SQUARE_RADIUS_MIN

	ps = PointStream()

	SQUARE = Square(0, 0, SQUARE_R, SQUARE_G, SQUARE_B,
			radius = SQUARE_RADIUS_MIN)

	SQUARE.x = SQUARE_X
	SQUARE.y = SQUARE_Y

	ps.objects.append(SQUARE)

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

def spin_thread():
	global SQUARE
	global SQUARE_X, SQUARE_Y
	global SQUARE_RADIUS_MIN, SQUARE_RADIUS_MAX
	global SQUARE_RADIUS_INC
	global SPIN_THETA_INC
	global PAN_X_INC_MAG, PAN_X_MAX, PAN_X_MIN

	inc = True
	panInc = True

	xPan = 0
	spin = 0

	while True:

		# RADIUS
		r = SQUARE.radius
		if r > SQUARE_RADIUS_MAX:
			inc = False
		elif r < SQUARE_RADIUS_MIN:
			inc = True

		if inc:
			r += SQUARE_RADIUS_INC
		else:
			r -= SQUARE_RADIUS_INC

		SQUARE.radius = r

		# PAN
		if xPan > PAN_X_MAX:
			panInc = False
		elif xPan < PAN_X_MIN:
			panInc = True

		if panInc:
			xPan += PAN_X_INC_MAG
			spin = -SPIN_THETA_INC
		else:
			xPan -= PAN_X_INC_MAG
			spin = SPIN_THETA_INC

		SQUARE.x = SQUARE_X + xPan
		SQUARE.theta += spin

		time.sleep(0.05)

#
# Start Threads
#

SQUARE = Square()

thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(spin_thread, ())

while True:
	time.sleep(100000)

