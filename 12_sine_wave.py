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

from daclib import dac
from daclib.common import *

from common.stream import PointStream
from common.shape import Shape

"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

ORIGIN_X = 0
ORIGIN_Y = 6000

COLOR_R = CMAX / 1
COLOR_G = CMAX / 1
COLOR_B = CMAX / 1

WAVE_SAMPLE_PTS = 500
WAVE_PERIODS = 3
WAVE_RATE = 1
WAVE_WIDTH = 24000 # XXX Not wavelength!
WAVE_AMPLITUDE_MAGNITUDE = 6000 # dither between +/-
WAVE_AMPLITUDE_RATE = 500

"""
CODE BEGINS HERE
"""

class SineWave(Shape):

	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0,
			width = 10000, height = 2200):

		super(SineWave, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.height = height
		self.width = width

		self.sineAmp = 2000
		self.sinePos = 0
		self.numPeriods = 4

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		# Generate points
		lx = - self.width / 2

		rh = self.r / 8
		bh = self.b / 8

		for i in xrange(0, WAVE_SAMPLE_PTS, 1):
			periods = self.numPeriods * 2 * math.pi
			percent = float(i) / WAVE_SAMPLE_PTS

			x = lx + int(self.width* percent) + self.x
			i = (percent * periods) + self.sinePos
			y = int(math.sin(i) * self.sineAmp) + self.y

			r = int(self.g - rh*percent)
			g = self.g
			b = int(self.b - bh + bh*percent)

			s = (x, y, r, g, b)
			if s[0] == 0 or s[1] == 0:
				continue # XXX DEBUG
			yield s

		"""
		math.sin(i)

		pts = []
		pts.append({'x': ed, 'y': ed})
		pts.append({'x': -ed, 'y': ed})
		pts.append({'x': -ed, 'y': -ed})
		pts.append({'x': ed, 'y': -ed})

		# Rotate points
		for p in pts:
			x = p['x']
			y = p['y']
			p['x'] = x*math.cos(self.theta) - y*math.sin(self.theta)
			p['y'] = y*math.cos(self.theta) + x*math.sin(self.theta)

		# Translate points
		for pt in pts:
			pt['x'] += self.x
			pt['y'] += self.y

		r = 0 if not self.r else int(self.r / LASER_POWER_DENOM)
		g = 0 if not self.g or LASER_POWER_DENOM > 4 else self.g
		b = 0 if not self.b else int(self.b / LASER_POWER_DENOM)

		def make_line(pt1, pt2, steps=200):
			xdiff = pt1['x'] - pt2['x']
			ydiff = pt1['y'] - pt2['y']
			line = []
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = pt1['x'] - (xdiff * j)
				y = pt1['y'] - (ydiff * j)
				line.append((x, y, r, g, b)) # XXX FIX COLORS
			return line

		# DRAW THE SHAPE

		p = None # Save in scope

		for p in make_line(pts[0], pts[1], SQUARE_EDGE_SAMPLE_PTS):
			break
		for i in range(int(round(SQUARE_VERTEX_SAMPLE_PTS/2.0))):
			yield p
		for p in make_line(pts[0], pts[1], SQUARE_EDGE_SAMPLE_PTS):
			yield p
		for i in range(SQUARE_VERTEX_SAMPLE_PTS):
			yield p
		for p in make_line(pts[1], pts[2], SQUARE_EDGE_SAMPLE_PTS):
			yield p
		for i in range(SQUARE_VERTEX_SAMPLE_PTS):
			yield p
		for p in make_line(pts[2], pts[3], SQUARE_EDGE_SAMPLE_PTS):
			yield p
		for i in range(SQUARE_VERTEX_SAMPLE_PTS):
			yield p
		for p in make_line(pts[3], pts[0], SQUARE_EDGE_SAMPLE_PTS):
			self.lastPt = p # KEEP BOTH
			yield p
		for i in range(int(round(SQUARE_VERTEX_SAMPLE_PTS/2.0))):
			self.lastPt = p # KEEP BOTH
			yield p

		"""

		self.drawn = True

def dac_thread():
	global SINEW
	global WAVE_PERIODS

	ps = PointStream()
	#ps.showTracking = True
	#ps.showBlanking = True
	ps.trackingSamplePts = 50
	ps.blankingSamplePts = 50

	SINEW = SineWave(0, 0, COLOR_R/LASER_POWER_DENOM,
							COLOR_G/LASER_POWER_DENOM,
							COLOR_B/LASER_POWER_DENOM)

	SINEW.numPeriods = WAVE_PERIODS
	SINEW.width = WAVE_WIDTH
	SINEW.sineAmp = WAVE_AMPLITUDE_MAGNITUDE

	SINEW.x = ORIGIN_X
	SINEW.y = ORIGIN_Y

	#SQUARE.x = SQUARE_X
	#SQUARE.y = SQUARE_Y

	ps.objects.append(SINEW)

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

def animate_thread():
	global SINEW

	inc = True
	panInc = True

	xPan = 0
	spin = 0

	ampDirec = 1

	while True:
		# Translation rate animation
		SINEW.sinePos += WAVE_RATE
		time.sleep(0.015)

		#  Amplitude shift animation
		if SINEW.sineAmp > \
				WAVE_AMPLITUDE_MAGNITUDE:
			ampDirec = -1
		elif SINEW.sineAmp < \
				-WAVE_AMPLITUDE_MAGNITUDE:
			ampDirec = 1
		if ampDirec >= 0:
			SINEW.sineAmp += WAVE_AMPLITUDE_RATE
		else:
			SINEW.sineAmp -= WAVE_AMPLITUDE_RATE

#
# Start Threads
#

SINEW = SineWave()

thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(animate_thread, ())

while True:
	time.sleep(100000)

