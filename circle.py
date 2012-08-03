# XXX: THERE IS A BAD COLOR ERROR

import dac
import math

CMAX = 65535 # MAX COLOR VALUE

class LinePointStream(object):

	PTMAX = 32600

	def __init__(self, x1, y1, x2, y2, r=0, g=0, b=0):
		self.x1 = x1
		self.y1 = y1
		self.x2 = x2
		self.y2 = y2
		self.r = r
		self.g = g
		self.b = b

		self.stream = self.produce()

	def produce(self):
		xdiff = self.x2 - self.x1
		ydiff = self.y2 - self.y1

		steps = 100

		print self.x1
		print self.x2

		while True:
			# Line out
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = self.x1 + (xdiff * j)
				y = self.y1 + (ydiff * j)
				yield (x, y, self.r, self.g, self.b)

			# Line back in
			for i in xrange(0, steps, 1):
				j = float(i)/steps
				x = self.x2 - xdiff * j
				y = self.y2 - ydiff * j
				yield (x, y, self.r, self.g, self.b)

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d


class CirclePointStream(object):

	"""
	def produce(self):
		if self.called:
			return 
		self.called = True

		pmax = 32600
		pmax = 4000 # XXX
		pstep = 3
		cmax = 65535 # MAX COLOR VALUE
		cmin = cmax / 4
		do = True
		while do:
			# XXX TUPLE: (x, y, r, g, b)
			for x in xrange(-pmax, pmax, pstep): # top
				yield (x, pmax, 0, 0, 0) 
			for y in xrange(pmax, -pmax, -pstep): # left
				yield (pmax, y, 0, cmax, 0)
			for x in xrange(pmax, -pmax, -pstep): # bottom
				yield (x, -pmax, 0, 0, 0)
			for y in xrange(-pmax, pmax, pstep): # right
				yield (-pmax, y, 0, cmax, 0)

			do = False
	"""

	def produce(self):

		MAXRAD =  32600

		USERAD = MAXRAD / 8
	
		RESIZE_SPEED_INV  = 300

		while True: 
			"""
			rad = USERAD
			for i in xrange(0, 1000, 1):
				i = float(i) / 1000 * 2 * math.pi
				x = int(math.cos(i) * rad)
				y = int(math.sin(i) * rad) 
				yield (x, y, 0, 0, CMAX) 

			for i in xrange(0, 1000, 1):
				i = float(i) / 1000 * 2 * math.pi
				x = int(math.cos(i) * rad) + 1000
				y = int(math.sin(i) * rad) + 1000
				yield (x, y, 0, 0, CMAX)

			# Blank
			yield (0, 0, 0, 0, 0)
			"""
			pass

	def __init__(self):
		self.called = False
		self.stream = self.produce()

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

class NullPointStream(object):
	def read(self, n):
		return [(0, 0, 0, 0, 0)] * n

d = dac.DAC("169.254.206.40")

#ps = LinePointStream(-5000, -5000, 5000, 5000, b=CMAX)
ps = LinePointStream(5000, 5000, -10000, -10000, b=CMAX)
d.play_stream(ps)

