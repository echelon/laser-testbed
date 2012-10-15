#!/usr/bin/env python

import os
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

"""
Globals
"""

objs = []
obj = None
ps = None


"""
Animation code / logic
"""

class SvgPath(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0, coords=None):
		super(SvgPath, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.coords = coords

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		for c in self.coords:
			#x = math.floor(float(c['x']) * MULT_X) + ADD_X
			#y = math.floor(float(c['y']) * MULT_Y) + ADD_Y
			x = c['x'];
			y = c['y'];
			yield(int(x), int(y), CMAX, CMAX, CMAX)

		self.drawn = True

class Svg(Shape):

	def __init__(self, x = 0, y = 0,
			r = 0, g = 0, b = 0, cords=None):
		super(Svg, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		"""
		for c in self.cords:
			x = math.floor(float(c['x']) * 10)
			y = math.floor(float(c['y']) * 10)
			print x, y

			#yield(0, 0, CMAX, CMAX, CMAX)
			yield(int(x), int(y), CMAX, CMAX, CMAX)
		"""

		for i in range(len(OBJECTS)): #obj in OBJECTS:
			obj = OBJECTS[i]
			for pt in obj:
				x = math.floor(pt['x'] * 20)
				y = math.floor(pt['y'] * 20)
				yield(int(x), int(y), CMAX, CMAX, CMAX)



		self.drawn = True

def dac_thread():
	global objs
	global ps

	for obj in objs:
		ps.objects.append(obj)

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
	global objs
	global ps

	# XXX: Insecure!!
	modname = 'awesome'
	if len(sys.argv) > 1:
		modname = sys.argv[1]

	exec "from objs.%s import OBJECTS" % modname
	exec "from objs.%s import MULT_X, MULT_Y" % modname
	exec "from objs.%s import ADD_X, ADD_Y" % modname

	for i in range(len(OBJECTS)): #obj in OBJECTS:
		coords = OBJECTS[i]

		# Normalize/fix coordinate system
		for j in range(len(coords)):
			c = coords[j]
			x = math.floor(float(c['x']) * MULT_X) + ADD_X
			y = math.floor(float(c['y']) * MULT_Y) + ADD_Y
			coords[j] = {'x': x, 'y': y};

		OBJECTS[i] = coords
		objs.append(SvgPath(coords=coords))

	ps = PointStream()
	#ps.showBlanking = True
	#ps.showTracking = True
	ps.blankingSamplePts = 30
	ps.trackingSamplePts = 30

	thread.start_new_thread(dac_thread, ())
	time.sleep(1.0)
	#thread.start_new_thread(spin_thread, ())

	while True:
		time.sleep(100000)

if __name__ == '__main__':
	main()
