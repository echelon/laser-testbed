#!/usr/bin/env python

"""
A line for beam shows that animates.
Started Dec 1, 2012
"""

from lib import dac
from lib.common import *
from lib.shape import Shape
from lib.stream import PointStream
from lib.system import *

# TODO: Shape needs to be standardized to support
# scaling, rotation, etc. out of the box in the same
# way for all shapes.

class Line(Shape):

	def __init__(self, x = 0, y = 0,
					r = CMAX, g = CMAX, b = CMAX,
					length = 10000):

		super(Line, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.samplePoints = 300
		self.length = length
		self.direc = True

	def produce(self):

		half = self.length / 2
		start = -half
		end = half
		step = self.length/(self.samplePoints*1.0)

		for i in xrange(self.samplePoints):
			x = start + step*i
			y = self.y
			yield(x, y, self.r, self.g, self.b)

		start = half
		end = -half
		step *= -1

		for i in xrange(self.samplePoints):
			x = start + step*i
			y = self.y
			yield(x, y, self.r, self.g, self.b)

		self.drawn = True

OBJ = None

def dac_thread():
	global OBJ

	ps = PointStream()

	OBJ = Line()
	ps.objects.append(OBJ)

	ps.showBlankingPath = True
	ps.showTrackingPath = True

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

def move_thread():

	plus = 100
	topLimit = 30000
	bottomLimit = 20000

	OBJ.length = 6000
	OBJ.y = (topLimit + bottomLimit)/2

	while True:
		OBJ.y += plus

		if OBJ.y > topLimit:
			print 'top'
			plus *= -1

		elif OBJ.y < bottomLimit:
			print 'bottom'
			plus *= -1

		time.sleep(0.04)

thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(move_thread, ())

while True:
	time.sleep(100000)

