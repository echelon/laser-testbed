#!/usr/bin/env python

"""
A rotating, translating, transforming (growing) square.
Integrates some code from my GameJam project, Laser Asteroids.
"""

import math
import random
import itertools
import sys
import time
import thread

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.shape import Shape
from lib.color import *

"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

ORIGIN_X = 0
ORIGIN_Y = 0

COLOR_R = CMAX / 1
COLOR_G = CMAX / 1
COLOR_B = CMAX / 1

WAVE_SAMPLE_PTS = 500
WAVE_PERIODS = 4
WAVE_RATE = 0.6
WAVE_WIDTH = 42000 # XXX Not wavelength!
WAVE_AMPLITUDE_MAGNITUDE = 15000 # dither between +/-
WAVE_AMPLITUDE_RATE = 900

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

			# XXX FIX MATHS: Something wrong, 
			# but does it matter?
			r = int(abs(math.floor(self.g -
						rh*percent)))
			g = abs(self.g)
			b = int(abs(math.floor(self.b -
						bh + bh*percent)))

			s = (x, y, r, g, b)
			if s[0] == 0 or s[1] == 0:
				continue # XXX DEBUG
			yield s

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

def color_thread():
	global SINEW

	rr = DitherColor(inc = random.randint(500, 5000))
	gg = DitherColor(inc = random.randint(500, 5000))
	bb = DitherColor(inc = random.randint(500, 5000))

	# Unfortunately, my red laser is out of commission
	rr.min = CMAX - 1
	rr.max = CMAX
	gg.min = CMAX / 2
	gg.max = CMAX
	bb.min = CMAX / 3
	bb.max = CMAX

	color = RandomColorAnimation()

	while True:
		rr.incr()
		gg.incr()
		bb.incr()
		color.frame()

		#SINEW.r = color.curColor.r
		#SINEW.g = color.curColor.g
		#SINEW.b = color.curColor.b

		SINEW.r = int(rr.getVal())
		SINEW.g = int(gg.getVal())
		SINEW.b = int(bb.getVal())

		time.sleep(0.1)



#
# Start Threads
#

SINEW = SineWave()

thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(animate_thread, ())
thread.start_new_thread(color_thread, ())

while True:
	time.sleep(100000)

