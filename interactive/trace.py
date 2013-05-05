#!/usr/bin/env python

"""
A game controller draws a line, the projector follows.
Started May 5, 2013
"""

from lib import dac
from lib.common import *
from lib.shape import Shape
from lib.stream import PointStream
from lib.system import *
from lib.controller import *

SIMPLE_TRANSLATION_SPD = 1000
MAX_X = 25000
MAX_Y = 25000
MIN_X = - MAX_X
MIN_Y = - MAX_Y

MAX_LENGTH = 150

# TODO: Shape needs to be standardized to support
# scaling, rotation, etc. out of the box in the same
# way for all shapes.

class Tracer(Shape):

	def __init__(self, x = 0, y = 0,
					r = CMAX, g = CMAX, b = CMAX,
					length = 10000):

		super(Tracer, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.path = [{'x': 0, 'y': 0}]

		self.direc = True

	def addPoint(self, x, y):
		pt = {'x': x, 'y': y}
		while len(self.path) > MAX_LENGTH:
			self.path.pop(0)

		self.path.append(pt)

	def lastPoint(self):
		return self.path[-1]

	def produce(self):
		for pt in self.path:
			yield(pt['x'], pt['y'], self.r, self.g, self.b)
		self.drawn = True

OBJ = Tracer()

def dac_thread():
	global OBJ

	ps = PointStream()
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


def controller_thread():
	"""Manage the joysticks with PyGame"""
	global OBJ

	controller = init_controls()

	while True:
		e = controller.getEvent()

		lVert, lHori, rVert, rHori = (0, 0, 0, 0)
		x, y = (0, 0)

		lVert = controller.getLeftVert()
		lHori = controller.getLeftHori()
		rVert = controller.getRightVert()
		rHori = controller.getRightHori()

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

		#if newX != lastPt['x'] or newY != lastPt['y']:
		OBJ.addPoint(newX, newY)

		# Player rotation
		t = math.atan2(lVert, lHori)
		OBJ.theta = t

		# Keep this thread from hogging CPU
		time.sleep(0.02)


thread.start_new_thread(controller_thread, ())
time.sleep(1.0)
thread.start_new_thread(dac_thread, ())

while True:
	time.sleep(100000)

