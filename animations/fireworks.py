#!/usr/bin/env python

"""
Fireworks show!
Forked from flicker.py
Started May 30, 2013
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

"""# XXX OVERRIDE
X_MAX = 30000
X_MIN = -30000
Y_MAX = 30000
Y_MIN = -30000
"""

"""
CONFIGURATION
"""

# FIXME: Color generation code is really bad

LASER_POWER_DENOM = 1.0

NUM_FIREWORKS = 5 # Typically 5

VEL_MIN = 150 # Typically 150
VEL_MAX = 400 # Typically 400
ACCEL = 0.15 # Typically 0.15

EMBER_NUM_SAMPLE_PTS = 15
TRACKING_SAMPLE_PTS = 10
BLANKING_SAMPLE_PTS = 15

EMBERS_MIN = 4
EMBERS_MAX = 10

"""
GLOBALS
"""

PS = PointStream()
#PS.scale = 0.12
PS.translateX = 0
PS.translateY = 0
PS.trackingSamplePts = TRACKING_SAMPLE_PTS
PS.blankingSamplePts = BLANKING_SAMPLE_PTS

fireworks = []

class COLORS(object):
	WHITE = 'white'
	WHITE_GREEN = 'white/green'
	WHITE_BLUE = 'white/blue'
	GREEN_BLUE= 'green/blue'
	GREEN = 'green'
	BLUE = 'blue'
	ALL = 'all'

class Ember(Shape):

	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0):
		super(Ember, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.theta = 0
		self.thetaRate = 0

		self.xVel = 0
		self.yVel = 0

		self.xAccel = 0
		self.yAccel = 0

		self.timeStarted = datetime.datetime.now()
		self.lifetime = datetime.timedelta(
							seconds=random.uniform(0.0500, 3.000))

		self.alive = True

		self.cachedId = -1 # XXX: Not Stream API! Only this script!

	def produce(self):
		r, g, b = (0, 0, 0)

		r = 0 if not self.r else int(self.r / LASER_POWER_DENOM)
		g = 0 if not self.g or LASER_POWER_DENOM > 4 else self.g
		b = 0 if not self.b else int(self.b / LASER_POWER_DENOM)

		p = (self.x, self.y, r, g, b)
		for i in range(EMBER_NUM_SAMPLE_PTS):
			yield p

		self.drawn = True

	def tick(self):
		if self.yAccel != 0:
			self.x += self.xVel
			self.y += self.yVel

		self.yVel -= int(self.yAccel)
		self.yAccel += ACCEL

		pass

class Firework(object):

	def __init__(self, x=0, y=0, color=COLORS.ALL, numEmbers=5):

		self.timeStarted = datetime.datetime.now()
		self.lifetime = datetime.timedelta(
							seconds=random.uniform(0.7000, 3.000))

		self.color = color
		self.x = x
		self.y = y
		self.embers = []

		self.alive = True

		for i in range(numEmbers):
			xVel = random.randint(VEL_MIN, VEL_MAX)
			yVel = random.randint(VEL_MIN, VEL_MAX)

			if random.randint(0, 1):
				xVel *= -1

			if random.randint(0, 1):
				yVel *= -1

			ember = Ember(x, y)
			ember.xVel = xVel
			ember.yVel = yVel

			ember.r = 0
			ember.g = 0
			ember.b = 0

			if self.color == COLORS.WHITE:
				ember.r = CMAX
				ember.g = CMAX
				ember.b = CMAX
			elif self.color == COLORS.BLUE:
				ember.b = CMAX
			elif self.color == COLORS.GREEN:
				ember.g = CMAX
			elif self.color == COLORS.WHITE_GREEN:
				if random.randint(0, 1):
					ember.r = CMAX
					ember.g = CMAX
					ember.b = CMAX
				else:
					ember.g = CMAX
			elif self.color == COLORS.WHITE_BLUE:
				if random.randint(0, 1):
					ember.r = CMAX
					ember.g = CMAX
					ember.b = CMAX
				else:
					ember.b = CMAX
			elif self.color == COLORS.GREEN_BLUE:
				if random.randint(0, 1):
					ember.g = CMAX
				else:
					ember.b = CMAX
			elif self.color == COLORS.ALL:
				r = random.randint(0, 2)
				if r == 0:
					ember.g = CMAX
				elif r == 1:
					ember.b = CMAX
				else:
					ember.r = CMAX
					ember.g = CMAX
					ember.b = CMAX

			# XXX/TEMPORARY: ALL BLUE
			#ember.r = CMAX
			#ember.g = CMAX
			#ember.b = CMAX

			self.embers.append(ember)

		# Automatically register with PointStream
		# Perhaps this is the wrong place to handle this...
		keys = PS.addObjects(self.embers)
		for i in range(len(keys)):
			self.embers[i].cachedId = keys[i]

	def tick(self):
		stillAlive = False
		cullObjs = []

		for ember in self.embers:
			cull = False

			if not ember.alive:
				continue

			ember.tick()

			# Cull ember if out of bounds
			if ember.x > X_MAX or ember.x < X_MIN:
				cull = True
			elif ember.y > Y_MAX or ember.y < Y_MIN:
				cull = True

			# Cull ember if time is up
			elif False:
				pass

			if cull:
				cullObjs.append(ember.cachedId)
				ember.skipDraw = False
				ember.alive = False
			else:
				stillAlive = True

		# Remove from PointStream
		# Perhaps this is the wrong place to do this...
		if cullObjs:
			PS.removeObjects(cullObjs)

		if not stillAlive:
			self.alive = False

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
	global fireworks

	while True:
		for fw in fireworks:
			fw.tick()

		time.sleep(0.01)

def shoot_thread():
	global PS
	global fireworks

	while True:
		#now = datetime.datetime.now()

		while len(fireworks) < NUM_FIREWORKS:
			x = random.randint(int(X_MIN), int(X_MAX))
			y = random.randint(int(Y_MIN), int(Y_MAX))

			# TODO: Random color
			r = random.randint(0, 2)
			color = COLORS.GREEN
			if r == 0:
				color = COLORS.GREEN
			elif r == 1:
				color = COLORS.WHITE
			elif r == 2:
				color = COLORS.GREEN_BLUE

			numEmbers = random.randint(EMBERS_MIN, EMBERS_MAX)

			fw = Firework(x, y, color=color, numEmbers=numEmbers)
			fireworks.append(fw)

		i = 0
		while i < len(fireworks):
			fw = fireworks[i]
			if not fw.alive:
				fireworks.pop(i)

			i += 1

		time.sleep(0.01)

#
# Start Threads
#

thread.start_new_thread(dac_thread, ())
time.sleep(1.0)
thread.start_new_thread(anim_thread, ())
thread.start_new_thread(shoot_thread, ())

while True:
	time.sleep(100000)

