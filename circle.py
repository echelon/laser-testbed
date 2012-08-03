# XXX: THERE IS A BAD COLOR ERROR

import dac
import math

CMAX = 65535 # MAX COLOR VALUE

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

		USERAD = MAXRAD 
	
		RESIZE_SPEED_INV  = 300

		while True: 
			for j in xrange(0, RESIZE_SPEED_INV): # constant # sample pts
				l = abs(math.sin(float(j)/RESIZE_SPEED_INV* math.pi * 2))
				rad = USERAD / ( 1 + l*8 )
				for i in xrange(0, 1000, 1):
					i = float(i) / 1000 * 2 * math.pi
					x = int(math.cos(i) * rad)
					y = int(math.sin(i) * rad) 
					yield (x, y, 0, 0, CMAX) 

				for i in xrange(0, 1000, 1):
					i = float(i) / 1000 * 2 * math.pi
					x = int(math.cos(i) * rad) + 100
					y = int(math.sin(i) * rad) + 100
					yield (x, y, 0, 0, CMAX)


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
d.play_stream(CirclePointStream())

