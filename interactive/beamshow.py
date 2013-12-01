#!/usr/bin/env python

"""
A game controller draws a line, the projector follows.
Started May 5, 2013
"""

from datetime import datetime, timedelta

from lib import dac
from lib.common import *
from lib.shape import Shape
from lib.stream import PointStream
from lib.system import *
from lib.controller import *

BLINK = True # XXX: Cool! Blinking effect.

SIMPLE_TRANSLATION_SPD = 1000 # 1000
MAX_X = 320
MAX_Y = 100
MIN_X = - MAX_X
MIN_Y = -500

MAX_WIDTH = 30000
MIN_WIDTH = 30
WIDTH_INC = 2000
Y_INC = 1000

MAX_LENGTH = 450
MAX_BREAKS = 10

# TODO: Shape needs to be standardized to support
# scaling, rotation, etc. out of the box in the same
# way for all shapes.

class Beam(Shape):

	def __init__(self, x = 0, y = 0, r = CMAX, g = CMAX, b = CMAX):

		super(Beam, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0
		self.direc = True

		# BEAM DATA
		self.width = (MAX_WIDTH + MIN_WIDTH)/2
		self.numBreaks = 0


	def moveUp(self):
		print self.y
		if self.y + Y_INC > MAX_Y:
			self.y = MAX_Y

		self.y += Y_INC

	def moveDown(self):
		if self.y - Y_INC > MIN_Y:
			self.y = MIN_Y

		self.y -= Y_INC

	def moreLength(self):
		if self.width + WIDTH_INC >= MAX_WIDTH:
			self.width = MAX_WIDTH

		self.width += WIDTH_INC

	def lessLength(self):
		if self.width - WIDTH_INC <= MIN_WIDTH:
			self.width = MIN_WIDTH

		self.width -= WIDTH_INC

	def produce(self):
		POINTS = 1000
		STEP = 100
		startPt = -(self.width / 2)
		if self.width > 100:
			for i in xrange(POINTS):
				perc = (i/float(POINTS))

				x = startPt + (self.width * perc)
				y = self.y
				yield(x, y, CMAX, CMAX, CMAX)
			for i in xrange(self.width / STEP):
				x = startPt + i * STEP
				y = self.y
				yield(x, y, CMAX, CMAX, CMAX)
		else:
			for i in xrange(1000):
				x = self.x
				y = self.y
				yield (x, y, CMAX, CMAX, CMAX)

		self.drawn = True

beam = Beam()

def dac_thread():
	global beam

	ps = PointStream()
	ps.objects.append(beam)

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


def controller_thread():
	"""Manage the joysticks with PyGame"""
	global beam

	T_OFF = [0.0, -1.0]
	WAIT = timedelta(milliseconds=300)

	controller = init_controls()

	lastLTrigger = datetime.now()

	while True:
		e = controller.getEvent()

		lVert, lHori, rVert, rHori = (0, 0, 0, 0)
		x, y = (0, 0)

		lVert = controller.getLeftVert()
		#lHori = controller.getLeftHori()
		#rVert = controller.getRightVert()
		rHori = controller.getRightHori()
		lt = controller.getLeftTrigger()
		rt = controller.getRightTrigger()


		# Use triggers to toggle blink

		if lt not in T_OFF:
			print "less"
			beam.lessLength()
		if rt not in T_OFF:
			print "more"
			beam.moreLength()

		if lVert < 0:
			beam.moveUp()
		elif lVert > 0:
			beam.moveDown()

		"""
		if datetime.now() < lastLTrigger + WAIT:
			print "asdf"
			if lt not in T_OFF:
				print lt
				beam.moreLength()
				print "Press"
				lastLTrigger = datetime.now()
			else:
				print "Nopress"
		"""

		# Keep this thread from hogging CPU
		time.sleep(0.02)


thread.start_new_thread(controller_thread, ())
time.sleep(3.0)
thread.start_new_thread(dac_thread, ())

while True:
	time.sleep(100000)

