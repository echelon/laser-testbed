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

from daclib import dac
from daclib.common import *

from common.stream import PointStream
from common.shape import Shape

"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

POINT_NUM_SAMPLE_PTS = 30

BLINK_FACTOR = 7 # 1 in X chance it will not draw

NUM_POINTS = 8

X_MIN = -8000
X_MAX = 8000
Y_MIN = -8000
Y_MAX = 8000

TRACKING_SAMPLE_PTS = 7
BLANKING_SAMPLE_PTS = 12

"""
CODE BEGINS HERE
"""

class Point(Shape):

	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0):
		super(Point, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.life = 10

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		# Randomly off sometimes
		if random.randint(0, BLINK_FACTOR) == 0:
			self.drawn = True
			self.life -= 1
			return

		r, g, b = (0, 0, 0)

		r = 0 if not self.r else int(self.r / LASER_POWER_DENOM)
		g = 0 if not self.g or LASER_POWER_DENOM > 4 else self.g
		b = 0 if not self.b else int(self.b / LASER_POWER_DENOM)

		p = (self.x, self.y, r, g, b)
		for i in range(POINT_NUM_SAMPLE_PTS):
			yield p

		self.drawn = True

		self.life -= 1
		if self.life <= 0:
			self.destroy = True

PS = PointStream()
PS.trackingSamplePts = TRACKING_SAMPLE_PTS
PS.blankingSamplePts = BLANKING_SAMPLE_PTS

def dac_thread():
	global PS
	while True:
		try:
			d = dac.DAC(dac.find_first_dac())
			d.play_stream(PS)

		except KeyboardInterrupt:
			sys.exit()

		except Exception as e:
			import sys, traceback
			print '\n---------------------'
			print 'Exception: %s' % e
			print '- - - - - - - - - - -'
			traceback.print_tb(sys.exc_info()[2])
			print "\n"

def anim_thread():
	global PS
	while True:
		if len(PS.objects) < NUM_POINTS:
			x = random.randint(X_MIN, X_MAX)
			y = random.randint(Y_MIN, Y_MAX)
			life = random.randint(4, 7)

			r = CMAX/3 if random.randint(0, 1) else CMAX
			g = 0 if random.randint(0, 1) else CMAX
			b = CMAX/3 if random.randint(0, 1) else CMAX

			pt = Point(x, y, r, g, b)
			pt.life = life
			PS.objects.append(pt)

		time.sleep(0.01)

#
# Start Threads
#

thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(anim_thread, ())

while True:
	time.sleep(100000)

