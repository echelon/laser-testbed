#!/usr/bin/env python

"""
Adapted from trace.py. Moves in a random trail.
Started May 25, 2013
"""

from lib import dac
from lib.common import *
from lib.shape import Shape
from lib.stream import PointStream
from lib.system import *
import datetime

BLINK = True # Blinking effect.

MAX_X = 32000
MAX_Y = 32000
MIN_X = -MAX_X
MIN_Y = -MAX_Y

DX_MAG = 250
DY_MAG = 250

MAX_LENGTH = 450

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
		self.direc = True

		self.path = [{'x': 0, 'y': 0}]
		self.blink = False

		self.dtChangedX = datetime.datetime.now()
		self.dtChangedY = datetime.datetime.now()
		self.velX = 0
		self.velY = 0
		self.secWaitX = 0.5 # seconds to maintain velocity
		self.secWaitY = 0.5

	def clearPoints(self):
		while(self.path):
			self.path.pop(0)

	def addPoint(self, x, y):
		pt = {'x': x, 'y': y}
		while len(self.path) > MAX_LENGTH:
			self.path.pop(0)

		self.path.append(pt)

	def lastPoint(self):
		return self.path[-1]

	def produce(self):
		if not self.blink:
			for pt in self.path:
				yield(pt['x'], pt['y'], self.r, self.g, self.b)
		else:
			i = 0
			for pt in self.path:
				i += 1
				j = i % 3
				if j == 0:
					yield(pt['x'], pt['y'], 0,0,0)
				elif j == 1:
					yield(pt['x'], pt['y'], self.r, self.g, self.b)
				else:
					yield(pt['x'], pt['y'], self.r, self.g, 0)

		self.drawn = True

OBJ = Tracer()
OBJ.clearPoints()
OBJ.addPoint((MAX_X + MIN_X)/2, (MAX_Y + MIN_Y)/2)

if BLINK:
	OBJ.blink = True

def dac_thread():
	global OBJ

	ps = PointStream()
	ps.objects.append(OBJ)

	ps.showBlankingPath = False
	ps.showTrackingPath = False
	ps.blankingSamplePts = 10
	ps.trackingSamplePts = 10

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
	global OBJ
	global MIN_X, MIN_Y, MAX_X, MAX_Y, DX_MAG, DY_MAG

	while True:
		lastPt = OBJ.lastPoint()
		newX = lastPt['x']
		newY = lastPt['y']

		now = datetime.datetime.now()
		xElap = now - OBJ.dtChangedX
		yElap = now - OBJ.dtChangedY

		if xElap > datetime.timedelta(seconds=OBJ.secWaitX):
			OBJ.dtChangedX = now
			OBJ.velX = random.randint(-DX_MAG, DX_MAG)
			OBJ.secWaitX = random.randint(3, 15)/10

		if yElap > datetime.timedelta(seconds=OBJ.secWaitY):
			OBJ.dtChangedY = now
			OBJ.velY = random.randint(-DY_MAG, DY_MAG)
			OBJ.secWaitY = random.randint(3, 15)/10

		newX = lastPt['x'] + OBJ.velX
		newY = lastPt['y'] + OBJ.velY

		if newX < MIN_X:
			newX = MIN_X
			OBJ.velX = DX_MAG
		elif newX > MAX_X:
			newX = MAX_X
			OBJ.velX = -DX_MAG

		if newY < MIN_Y:
			newY = MIN_Y
			OBJ.velY = DY_MAG
		elif newY > MAX_Y:
			newY = MAX_Y
			OBJ.velY = -DY_MAG

		OBJ.addPoint(newX, newY)

		# Keep this thread from hogging CPU
		time.sleep(0.005)


thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(move_thread, ())

while True:
	time.sleep(100000)

