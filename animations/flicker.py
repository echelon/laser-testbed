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
import datetime

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.shape import Shape
from dimensions import *

"""
CONFIGURATION
"""

LASER_POWER_DENOM = 1.0

NUM_POINTS = 50

POINT_NUM_SAMPLE_PTS = 500
TRACKING_SAMPLE_PTS = 10
BLANKING_SAMPLE_PTS = 50

class Point(Shape):

	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0):
		super(Point, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.timeStarted = datetime.datetime.now()
		self.lifetime = datetime.timedelta(
							seconds=random.uniform(0.0001, 0.115))

	def produce(self):
		r, g, b = (0, 0, 0)

		r = 0 if not self.r else int(self.r / LASER_POWER_DENOM)
		g = 0 if not self.g or LASER_POWER_DENOM > 4 else self.g
		b = 0 if not self.b else int(self.b / LASER_POWER_DENOM)

		p = (self.x, self.y, r, g, b)
		for i in range(POINT_NUM_SAMPLE_PTS):
			yield p

		self.drawn = True


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
		now = datetime.datetime.now()

		while len(PS.objects) < NUM_POINTS:
			x = random.randint(X_MIN, X_MAX)
			y = random.randint(Y_MIN, Y_MAX)

			"""
			r, g, b = (CMAX, 0, 0)

			z = random.randint(0, 2)

			if z == 0:
				g = CMAX
				b = CMAX
			elif z == 1:
				g = CMAX
			elif z == 2:
				b = CMAX
			"""

			r = CMAX
			b = CMAX
			g = CMAX

			pt = Point(x, y, r, g, b)
			PS.objects.append(pt)

		i = 0
		while i < len(PS.objects):
			obj = PS.objects[i]
			delta = now - obj.timeStarted
			if delta > obj.lifetime:
				obj.destroy = True
				PS.objects.pop(i)
				#i+=1
				#break
			i+=1

		time.sleep(0.01)

#
# Start Threads
#

thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(anim_thread, ())

while True:
	time.sleep(100000)

