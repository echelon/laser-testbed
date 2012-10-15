import random
import math

CMAX = 65535 # MAX COLOR VALUE
CMIN_DITHERER = 10000

DITHER_INC_MAX = 3000
DITHER_INC_MIN = 800

"""
Predefined laser colors
I'm not sure how this will look on other hardware.
"""

LASER_COLORS = {
	'red': (CMAX, 0, CMAX/4),
	'green': (0, CMAX, CMAX/3.2),
	'blue': (CMAX/4, CMAX, CMAX),
	'yellow': (CMAX, CMAX, 0),
	'orange': (CMAX, CMAX, CMAX/3), # MEH!
	'pink_cool': (CMAX/2, 0, CMAX),
	'pink_warm': (CMAX, 0, CMAX/3),
	'purple': (CMAX/3, 0, CMAX),
	'white': (CMAX/2, CMAX, CMAX/2.2),
}

class Color(object):
	"""Simple color struct."""
	def __init__(self, r=0, g=0, b=0, name=None):
		self.r = r
		self.g = g
		self.b = b

		if name and name in LASER_COLORS:
			c = LASER_COLORS[name]
			self.r = c[0]
			self.g = c[1]
			self.b = c[2]

	def __str__(self):
		return "<Color: %s, %s, %s>" % (self.r, self.g, self.b)

class RandomColorAnimation(object):
	def __init__(self):
		# The color we want to send the laser projector
		self.curColor = Color(name='white')

		# The in-between states
		self.lastColor = Color(name='white')
		self.nextColor = Color(name='orange')

		# Number of frames in each step
		self.numFrames = 10
		self.curFrame = 0

	def frame(self):
		"""
		Increment the color.
		"""
		rd = self.nextColor.r - self.lastColor.r
		gd = self.nextColor.g - self.lastColor.g
		bd = self.nextColor.b - self.lastColor.b

		frac = float(self.curFrame) / (self.numFrames-1)

		# XXX FIX MATHS: Something wrong, but does it matter?
		self.curColor.r = int(math.floor(self.lastColor.r + rd*frac))
		self.curColor.g = int(math.floor(self.lastColor.r + gd*frac))
		self.curColor.b = int(math.floor(self.lastColor.r + bd*frac))

		self.curFrame += 1
		if self.curFrame >= self.numFrames:
			self.curFrame = 0

			self.lastColor = self.curColor
			col = random.choice(LASER_COLORS.keys())
			col = LASER_COLORS[col]
			self.nextColor = Color(col[0], col[1], col[2])

class DitherColor(object):
	def __init__(self, val=CMAX, inc=1):
		self.val = val
		self.direc = -1
		self.inc = inc
		self.incMin = DITHER_INC_MIN
		self.incMax = DITHER_INC_MAX

		self.min = 0
		self.max = CMAX

	def incr(self):
		"""
		Linearly increment or decrement the color intensity.
		"""
		val = self.val

		if self.direc <= 0:
			val -= self.inc
			if val < self.min:
				val = self.min
				self.direc = 1
				self.randomizeRate()

		else:
			val += self.inc
			if val >= self.max:
				val = self.max
				self.direc = -1
				self.randomizeRate()

		if val < 0:
			val = 0

		self.val = val

	def getVal(self):
		return abs(int(self.val))

	def randomizeRate(self):
		self.inc = random.randint(self.incMin, self.incMax)


