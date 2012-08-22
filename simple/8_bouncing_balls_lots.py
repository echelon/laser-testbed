#!/usr/bin/env python

"""
Now trying to do many bouncing balls. 
Let's see how much we can throw at the projector.
"""

from daclib import dac
from daclib.common import * 
from common.gui import BallGui

import math
import random
import itertools
import sys

import thread
import time

"""
NASTY GLOBALS
The gui will alter these.
"""
LASER_POWER_DENOM = 1
SHOW_BLANKING_PATH = False 
BLANK_SAMPLE_PTS = 5 
BALL_SAMPLE_PTS = 60 # XXX: Needs to increase proportionally to radius
PAUSE_START_PTS = 8 # 8 seems optimum
PAUSE_END_PTS = 8 # 8 seems optimum
CIRCLE_ROTATIONS = 1
BOUNCE_VEL_MIN = 75 
BOUNCE_VEL_MAX = 500 
RADIUS_MIN = 500
RADIUS_MAX = 7000

NUM_BALLS = 8  # XXX: STARUP ADJUSTABLE ONLY

class Entity(object):
	"""
	Just an attempt at an OO interface.
	Nothing really fancy yet. 
	"""
	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0):
		self.x = x
		self.y = y
		self.r = r
		self.g = g
		self.b = b

		# Cached first and last points. 
		self.firstPt = 0
		self.lastPt = 0

	def produce(self):
		self.lastPt = (0, 0, 0, 0, 0)
		return self.lastPt

	def cacheFirstPt(self):
		"""
		I need to cache the first point generated so that I can 
		slowly advance the galvos to the next object without starting 
		drawing. 
		"""
		# XXX/FIXME: This is a hack (should I be using generators?)
		for x in self.produce():
			self.firstPt = x
			break


# TODO: Rename circle
class Ball(Entity):
	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0, radius = 1200):
		super(Ball, self).__init__(x, y, r, g, b)
		self.radius = radius
		self.drawn = False

		self.pauseFirst = True 
		self.pauseLast = True 

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		"""
		Figured it out! This is where the "tails" were coming from!
		We have to blank first with NO color. The lasers turn on before
		the galvos reach their destination. Duh. I had it figured in 
		reverse. 
		"""
		if self.pauseFirst:
			x = int(math.cos(0) * self.radius) + self.x
			y = int(math.sin(0) * self.radius) + self.y
			r = 0 if not self.r else int(CMAX / LASER_POWER_DENOM)
			g = 0 if not self.g or LASER_POWER_DENOM > 4 else CMAX
			b = 0 if not self.b else int(CMAX / LASER_POWER_DENOM)
			self.lastPt = (x, y, 0, 0, 0)
			for i in xrange(PAUSE_START_PTS):
				yield self.lastPt

		for i in xrange(BALL_SAMPLE_PTS):
			i = 2 * math.pi * float(i) / BALL_SAMPLE_PTS * CIRCLE_ROTATIONS 
			x = int(math.cos(i) * self.radius) + self.x
			y = int(math.sin(i) * self.radius) + self.y

			r = 0 if not self.r else int(CMAX / LASER_POWER_DENOM)
			g = 0 if not self.g or LASER_POWER_DENOM > 4 else CMAX
			b = 0 if not self.b else int(CMAX / LASER_POWER_DENOM)

			self.lastPt = (x, y, r, g, b)
			yield self.lastPt

		if self.pauseLast:
			# XXX: Crude hack for broken edge
			for i in xrange(PAUSE_END_PTS): 
				yield (self.firstPt[0], self.firstPt[1], r, g, b)

			for i in xrange(PAUSE_END_PTS):
				yield self.firstPt

		self.drawn = True

class Triangle(Entity):
	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0, radius = 1200):
		super(Triangle, self).__init__(x, y, r, g, b)
		self.radius = radius 
		self.drawn = False

		self.pauseFirst = True 
		self.pauseLast = True 

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		"""
		Figured it out! This is where the "tails" were coming from!
		We have to blank first with NO color. The lasers turn on before
		the galvos reach their destination. Duh. I had it figured in 
		reverse. 
		"""
		"""
		if self.pauseFirst:
			x = int(math.cos(0) * self.radius) + self.x
			y = int(math.sin(0) * self.radius) + self.y
			r = 0 if not self.r else int(CMAX / LASER_POWER_DENOM)
			g = 0 if not self.g or LASER_POWER_DENOM > 4 else CMAX
			b = 0 if not self.b else int(CMAX / LASER_POWER_DENOM)
			self.lastPt = (x, y, 0, 0, 0)
			for i in xrange(PAUSE_START_PTS):
				yield self.lastPt
		"""

		# Generate points
		pt1 = math.pi/2.0
		pt2 = math.pi*5.0/4.0
		pt3 = math.pi*7.0/4.0

		x1 = int(math.cos(pt1)* self.radius) + self.x
		y1 = int(math.sin(pt1)* self.radius) + self.y

		x2 = int(math.cos(pt2)* self.radius) + self.x 
		y2 = int(math.sin(pt2)* self.radius) + self.y

		x3 = int(math.cos(pt3)* self.radius) + self.x 
		y3 = int(math.sin(pt3)* self.radius) + self.y

		pt1 = {'x': x1, 'y': y1}
		pt2 = {'x': x2, 'y': y2}
		pt3 = {'x': x3, 'y': y3}

		def make_line(pt1, pt2, backward=False, steps = 25):
			xdiff = pt1['x'] - pt2['x']
			ydiff = pt1['y'] - pt2['y']
			line = []
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = pt1['x'] - (xdiff * j)
				y = pt1['y'] - (ydiff * j)
				line.append((x, y, CMAX/2, CMAX/2, CMAX/2)) # XXX FIX COLORS
			return line

		for p in make_line(pt1, pt2):
			yield p
		
		for p in make_line(pt2, pt3):
			yield p

		for p in make_line(pt3, pt1):
			self.lastPt = p
			yield p


		"""
		for i in xrange(BALL_SAMPLE_PTS):
			i = 2 * math.pi * float(i) / BALL_SAMPLE_PTS * CIRCLE_ROTATIONS 
			x = int(math.cos(i) * self.radius) + self.x
			y = int(math.sin(i) * self.radius) + self.y

			r = 0 if not self.r else int(CMAX / LASER_POWER_DENOM)
			g = 0 if not self.g or LASER_POWER_DENOM > 4 else CMAX
			b = 0 if not self.b else int(CMAX / LASER_POWER_DENOM)

			self.lastPt = (x, y, r, g, b)
			yield self.lastPt
		"""


		"""
		if self.pauseLast:
			# XXX: Crude hack for broken edge
			for i in xrange(PAUSE_END_PTS): 
				yield (self.firstPt[0], self.firstPt[1], r, g, b)

			for i in xrange(PAUSE_END_PTS):
				yield self.firstPt

		"""
		self.drawn = True

class PointStream(object):
	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def produce(self):
		"""
		This infinite loop functions as an infinite point generator.
		It generates points for both balls as well as the "blanking"
		that must occur between them.
		"""
		while True: 

			# Generate and cache the first points of the objects.
			# Necessary in order to slow down galvo tracking from 
			# ball-to-ball as we move to the next object. 
			for b in balls:
				b.cacheFirstPt()

			# Draw all the balls... 
			for i in range(len(balls)):
				curBall = balls[i]
				nextBall = balls[(i+1)%len(balls)]

				# Draw the ball
				if not curBall.drawn:
					yield curBall.firstPt # This was cached upfront
					for x in curBall.produce():
						yield x

				# Paint last pt for smoothness
				# XXX: Remove?
				for x in xrange(BLANK_SAMPLE_PTS):
					yield curBall.firstPt

				# Paint empty for smoothness
				# XXX: Remove? 
				for x in xrange(BLANK_SAMPLE_PTS):
					yield (curBall.lastPt[0], curBall.lastPt[1], 0, 0, 0)

				# Now, track to the next object. 
				lastX = curBall.lastPt[0]
				lastY = curBall.lastPt[1]
				xDiff = curBall.lastPt[0] - nextBall.firstPt[0]
				yDiff = curBall.lastPt[1] - nextBall.firstPt[1]
				mv = BLANK_SAMPLE_PTS
				for i in xrange(mv): 
					percent = i/float(mv)
					xb = int(lastX - xDiff*percent)
					yb = int(lastY - yDiff*percent)
					# If we want to 'see' the tracking path. 
					if SHOW_BLANKING_PATH: # FIXME: Rename 'tracking'
						yield (xb, yb, 0, CMAX, 0)
					else:
						yield (xb, yb, 0, 0, 0)

			# Reset ball state (nasty hack for point caching)
			for b in balls:
				b.drawn = False


							
	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

"""
Main Program
"""

balls = []
for i in range(NUM_BALLS):
	b = None
	if random.randint(0, 1):
		b = Ball(0, 0, 0, 0, CMAX, random.randint(RADIUS_MIN, RADIUS_MAX))
	else:
		b = Triangle(0, 0, 0, 0, CMAX, random.randint(RADIUS_MIN, RADIUS_MAX))
	balls.append(b)

ps = PointStream()

def dac_thread():
	while True:
		try:
			d = dac.DAC(dac.find_first_dac())
			d.play_stream(ps)
		except Exception as e:
			import sys, traceback
			print '\n---------------------'
			print 'Exception: %s' % e
			print '- - - - - - - - - - -'
			traceback.print_tb(sys.exc_info()[2])
			print "\n"
			pass

def move_thread():
	"""
	This thread increments the ball positions and randomizes ball 
	velocities when they "bounce" off the walls. 
	This is just so sloppy of me... don't judge.
	"""
	MAX_X = 20000
	MIN_X = -20000
	MAX_Y = 20000
	MIN_Y = -20000

	# TODO: Combine direction and velocity... 
	# TODO: Store directly in ball object... 
	direcs = []
	velos = []

	for i in range(len(balls)):
		direcs.append({'x': 0, 'y': 0})
		velos.append({'x': 500, 'y': 500})

	while True:
		try:
			for i in range(len(balls)):
				ball = balls[i]
				direc = direcs[i]
				velo = velos[i]

				# Bounce off wall
				if ball.x > MAX_X:
					direc['x'] = 0
					velo['x'] = random.randint(BOUNCE_VEL_MIN, BOUNCE_VEL_MAX)
				elif ball.x < MIN_X:
					direc['x'] = 1
					velo['x'] = random.randint(BOUNCE_VEL_MIN, BOUNCE_VEL_MAX)

				if ball.y > MAX_Y:
					direc['y'] = 0
					velo['y'] = random.randint(BOUNCE_VEL_MIN, BOUNCE_VEL_MAX)
				elif ball.y < MIN_Y:
					direc['y'] = 1
					velo['y'] = random.randint(BOUNCE_VEL_MIN, BOUNCE_VEL_MAX)

				if direc['x']:
					ball.x += velo['x']
				else:
					ball.x -= velo['x']

				if direc['y']:
					ball.y += velo['y']
				else:
					ball.y -= velo['y']

			time.sleep(0.020)

		except:
			continue

def change_params(adj, widget, window):
	global LASER_POWER_DENOM, BALL_SAMPLE_PTS, CIRCLE_ROTATIONS
	global PAUSE_START_PTS, PAUSE_END_PTS
	global BOUNCE_VEL_MAX, BOUNCE_VEL_MIN
	global RADIUS_A, RADIUS_B

	LASER_POWER_DENOM = window.laserPowDenom.get_value()
	BALL_SAMPLE_PTS = int(window.samplePts.get_value())
	PAUSE_START_PTS = int(window.pauseStartPts.get_value())
	PAUSE_END_PTS = int(window.pauseEndPts.get_value())
	CIRCLE_ROTATIONS = int(window.rotations.get_value())
	BOUNCE_VEL_MIN = int(window.bounceVelMin.get_value())
	BOUNCE_VEL_MAX = int(window.bounceVelMax.get_value())

	b1.radius = int(window.radiusA.get_value())
	b2.radius = int(window.radiusB.get_value())

def gui_thread():
	"""
	Start and manage the gui
	"""
	gui = BallGui()
	gui.install_cb(change_params)
	gui.main_loop()

thread.start_new_thread(dac_thread, ())
thread.start_new_thread(move_thread, ())
#thread.start_new_thread(gui_thread, ())

while True:
	time.sleep(20)


