#!/usr/bin/env python

"""
A simple game of Pong with PS3 controllers.

	PS3 Mappings
	------------
	Axis 0	- Left horiontal (-1 is up, 1 is down)
	Axis 1	- Left vertical
	Axis 2	- Right horizontal 
	Axis 3	- Right vertical 

	Button 4	- Up
	Button 5	- Right
	Button 6	- Down
	Button 7	- Left

	Button 12	- Triangle
	Button 13	- Circle
	Button 14	- X
	Button 15	- Square 

	Button 16	- PS Button

Use qtsixa to pair controllers, then sixad to start the bluetooth 
daemon.
"""

from daclib import dac
from daclib.common import *

import math
import random
import itertools
import sys

import thread
import time

import pygame

"""
NASTY GLOBALS
The gui will alter these.
"""
LASER_POWER_DENOM = 1
SHOW_BLANKING_PATH = False 
BLANK_SAMPLE_PTS = 12 

# XXX: Needs to increase proportionally to radius
BALL_SAMPLE_PTS = 20 
TRIANGLE_EDGE_SAMPLE_PTS = 20
SQUARE_EDGE_SAMPLE_PTS = 20 

PAUSE_START_PTS = 9 # 8 seems optimum
PAUSE_END_PTS = 9 # 8 seems optimum
CIRCLE_ROTATIONS = 1
BOUNCE_VEL_MIN = 75 
BOUNCE_VEL_MAX = 500 

PADDLE_WIDTH = 1000
PADDLE_HEIGHT = 2000
BALL_RADIUS = 1500

balls = [] # TODO: REFACTOR
PLAYERS = []

SIMPLE_TRANSLATION_SPD = 600

MAX_X = 25000
MIN_X = -25000
MAX_Y = 25000
MIN_Y = -25000


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

class Square(Entity):
	def __init__(self, x = 0, y = 0, r = 0, g = 0, b = 0, radius = 1200):
		super(Square, self).__init__(x, y, r, g, b)
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
		ed = self.radius/2

		x1 = self.x + ed
		y1 = self.y + ed
		x2 = self.x - ed
		y2 = self.y + ed
		x3 = self.x - ed
		y3 = self.y - ed
		x4 = self.x + ed
		y4 = self.y - ed
	
		pt1 = {'x': x1, 'y': y1}
		pt2 = {'x': x2, 'y': y2}
		pt3 = {'x': x3, 'y': y3}
		pt4 = {'x': x4, 'y': y4}

		r = 0 if not self.r else int(CMAX / LASER_POWER_DENOM)
		g = 0 if not self.g or LASER_POWER_DENOM > 4 else CMAX
		b = 0 if not self.b else int(CMAX / LASER_POWER_DENOM)

		def make_line(pt1, pt2, steps=200):
			xdiff = pt1['x'] - pt2['x']
			ydiff = pt1['y'] - pt2['y']
			line = []
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = pt1['x'] - (xdiff * j)
				y = pt1['y'] - (ydiff * j)
				line.append((x, y, r, g, b)) # XXX FIX COLORS
			return line

		for p in make_line(pt1, pt2, SQUARE_EDGE_SAMPLE_PTS):
			yield p
		
		for p in make_line(pt2, pt3, SQUARE_EDGE_SAMPLE_PTS):
			yield p

		for p in make_line(pt3, pt4, SQUARE_EDGE_SAMPLE_PTS):
			yield p

		for p in make_line(pt4, pt1, SQUARE_EDGE_SAMPLE_PTS):
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


"""
Main Program
"""

ps = PointStream()

def dac_thread():
	global PLAYERS

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

			# In case we went off edge, recenter. 
			# XXX: This is just laziness
			for p in PLAYERS:
				p.obj.x = 0
				p.obj.y = 0

class Player(object):
	"""
	Player (conflated)
		- Contain joystick ref
		- Contain visual object
	"""
	def __init__(self, joystick, radius=BALL_RADIUS, rgb=(CMAX, CMAX, CMAX)):
		self.js = joystick
		self.score = 0
		self.pid = 0

		# Joystick
		joystick.init()

		# Laser
		self.obj = Ball(0, 0, rgb[0], rgb[1], rgb[2], radius)
		balls.append(self.obj)
	
	def __str__(self):
		return self.js.get_name()

"""
Global objects
"""
def joystick_thread():
	"""Manage the joysticks with PyGame"""
	global PLAYERS

	pygame.joystick.init()
	pygame.display.init()
	
	if not pygame.joystick.get_count():
		print "No Joystick detected!"
		sys.exit()

	p1 = Player(pygame.joystick.Joystick(0))
	p2 = Player(pygame.joystick.Joystick(1))

	PLAYERS.append(p1)
	PLAYERS.append(p2)

	numButtons = p1.js.get_numbuttons() # XXX NO!

	while True:
		e = pygame.event.get()

		for p in PLAYERS:

			vel1 = p.js.get_axis(1) # Left joystick
			vel2 = p.js.get_axis(0)

			if vel1:
				y = p.obj.y
				y += -1 * int(vel1 * SIMPLE_TRANSLATION_SPD)
				if MIN_Y < y < MAX_Y:
					p.obj.y = y

			if vel2:
				x = p.obj.x
				x += -1 * int(vel2 * SIMPLE_TRANSLATION_SPD)
				if MIN_X < x < MAX_X:
					p.obj.x = x

		time.sleep(0.02) # Keep this thread from hogging CPU


thread.start_new_thread(joystick_thread, ())
thread.start_new_thread(dac_thread, ())

while True:
	time.sleep(20)


