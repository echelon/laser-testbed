"""
Svg Shapes -- Classes and functions to make working with
			  SVG graphics easier. This is going to take
			  a lot of work to bring to parity to what I
			  expect, which would be raw SVG files.
"""

import os
import math
import random
import itertools
import sys
import time
import thread
import copy
from datetime import datetime

from lib import dac
from lib.common import *
from lib.stream import PointStream
from lib.system import *
from lib.shape import Shape
from lib.importObj import importObj

"""
Animation Class
"""

class SvgAnim(AdvancedAnimation):
	"""
	Imports a script containing points extracted previously
	from SVG graphics files.
	VERY crude -- need to do direct SVG importing ASAP.
	"""

	def loadFile(self):
		# FIXME: Definitely a better way to do this...
		exec "from objs.%s import OBJECTS" % self.loadFilename
		exec "from objs.%s import MULT_X" % self.loadFilename
		exec "from objs.%s import MULT_Y" % self.loadFilename

		self.hasAnimationThread = False if not \
				self.animParams else True

		self.blankingSamplePts = 7
		self.trackingSamplePts = 15

		obj = load_svg(self.loadFilename)
		self.objects.append(obj)

		obj.setColor(self.r, self.g, self.b)

"""
Loading and Caching
"""

def load_svg(name, skip=3):
	"""
	Load a file containing parsed SVG geometry and return
	an SVG object (with one or more SvgPaths).
	"""
	objCoords = SvgCache.instance().get(name)
	paths = []

	for i in range(len(objCoords)):
		coords = objCoords[i]

		obj = SvgPath(coords=coords)
		obj.jitter = False
		obj.skip = skip

		paths.append(obj)

	return Svg(paths=paths)

class SvgCache(dict):

	_INSTANCE = None

	@classmethod
	def instance(self):
		if not SvgCache._INSTANCE:
			SvgCache._INSTANCE = SvgCache()

		return SvgCache._INSTANCE

	def get(self, k):
		if k in self:
			return self[k]

		# FIXME: Definitely a better way to do this...
		exec "from objs.%s import OBJECTS" % k
		exec "from objs.%s import MULT_X" % k
		exec "from objs.%s import MULT_Y" % k

		coordSets = importObj(OBJECTS, MULT_X, MULT_Y)
		self[k] = coordSets

		return coordSets

	def __setattr__(self, k, v):
		raise Exception, 'Cannot assign to SvgCache'

"""
Object / Shape / Stream
"""

class Svg(Shape):
	"""
	A cross between SHAPE and STREAM.
	Manages several SvgPath(Shape) objects in a Stream.
	"""

	def __init__(self, x = 0, y = 0,
			r = CMAX, g = CMAX, b = CMAX, paths=None):
		super(Svg, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		# Remove these? XXX
		self.showBlanking = False
		self.showTracking = False
		self.blankingSamplePts = 10
		self.trackingSamplePts = 10

		self.objects = paths # [SvgPath]s

		self.theta = 0
		self.thetaRate = 0
		self.scale = 1.0
		self.scaleX = None
		self.scaleY = None
		self.jitter = True

		self.drawEvery = 1
		self.drawIndex = 1

		self.skip = 0

		self.flipX = False
		self.flipY = False

	def setScaleIndep(self, x=1.0, y=1.0):
		self.scaleX = x
		self.scaleY = y

	def setColor(self, r=CMAX, g=CMAX, b=CMAX):
		"""
		Mutuator to set color for all SvgPaths.
		"""
		for obj in self.objects:
			obj.r = r
			obj.g = g
			obj.b = b

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		# Obect skipping algo
		self.drawIndex = (self.drawIndex+1) % self.drawEvery

		doDraw = True
		if not self.drawIndex in [0, 1]:
			doDraw = False

		if not doDraw:
			self.drawn = True
			return

		i = 0
		for svgPath in self.objects:
			if self.skip:
				i += 1
				if i % self.skip == 0:
					continue

			# FIXME: Hugely inefficient
			# TODO: Enforce use of accessor/mutator
			svgPath.scale = self.scale
			svgPath.scaleX = self.scaleX
			svgPath.scaleY = self.scaleY
			svgPath.theta = self.theta
			svgPath.flipX = self.flipX
			svgPath.flipY = self.flipY
			svgPath.x = self.x
			svgPath.y = self.y

			# TODO: Actual drawing and blanking!!
			#yield(int(x), int(y), self.r, self.g, self.b)

		#print "POINT STREAM LOOP BEGIN"
		curObj = None # XXX SCOPE HERE FOR DEBUG ONLY
		nextObj = None # XXX SCOPE HERE FOR DEBUG 
		reverse = False

		# XXX: Memory copy for opencv app
		objects = self.objects[:]

		# Reverse heuristic
		reverse = not reverse
		if reverse:
			objects.reverse()

		# Generate and cache the first points of the
		# objects. Necessary in order to slow down 
		# galvo tracking as we move to the next object.

		for b in objects:
			b.cacheFirstPt()

		# Objects to destroy at end of loop
		# TODO: Move this outside of object. 
		# TODO: Not PointStream's job
		destroy = []

		# Draw all the objects... 
		for i in range(len(objects)):
			curObj = objects[i]
			nextObj = objects[(i+1)%len(objects)]

			# Skip draw?
			if curObj.skipDraw:
				continue

			# Prepare to cull object if it is marked destroy
			# TODO: Move this outside of object. 
			# TODO: Not PointStream's job
			if curObj.destroy:
				destroy.append(i)

			# FIXME: This is done twice for all firstPts
			# Once here, twice for tracking to nextObj
			#firstPt = self.transform(curObj.firstPt)
			firstPt = curObj.firstPt

			# Blanking (on the way in), if set
			if curObj.doBlanking:
				p = firstPt
				p = (p[0], p[1], 0, 0, 0)
				# If we want to debug the blanking 
				if self.showBlanking:
					p = (p[0], p[1], _CMAX, 0, _CMAX)
				for x in range(self.blankingSamplePts):
					yield p

			# Draw the object
			lastPt = (0, 0, 0, 0, 0)
			if not curObj.drawn:
				# XXX: This was cached upfront!
				yield firstPt
				for pt in curObj.produce():
					#lastPt = self.transform(pt)
					lastPt = pt
					yield lastPt

			# Blanking (on the way out), if set
			if curObj.doBlanking:
				p = lastPt
				p = (p[0], p[1], 0, 0, 0)
				# If we want to debug the blanking 
				if self.showBlanking:
					p = (p[0], p[1], _CMAX, 0, _CMAX)
				for x in range(self.blankingSamplePts):
					yield p

			# Now, track to the next object. 
			# FIXME: inefficient
			# FIXME: nextObj.firstPt transformed 2x!
			#nextFirstPt = self.transform(nextObj.firstPt)
			nextFirstPt = nextObj.firstPt
			lastX = lastPt[0]
			lastY = lastPt[1]
			xDiff = lastPt[0] - nextFirstPt[0]
			yDiff = lastPt[1] - nextFirstPt[1]

			mv = self.trackingSamplePts
			for i in xrange(mv):
				percent = i/float(mv)
				xb = int(lastX - xDiff*percent)
				yb = int(lastY - yDiff*percent)
				# If we want to debug the tracking path 
				if self.showTracking:
					yield (xb, yb, 0, _CMAX, 0)
				else:
					yield (xb, yb, 0, 0, 0)

		# Reset object state (nasty hack for point caching)
		for b in objects:
			b.drawn = False

		# Items to destroy
		# TODO: Move this outside of object. 
		# TODO: Not PointStream's job
		destroy.sort()
		destroy.reverse()
		for i in destroy:
			objects.pop(i)

		self.drawn = True

class SvgPath(Shape):

	def __init__(self, x = 0, y = 0,
			r = CMAX, g = CMAX, b = CMAX, coords=None):
		super(SvgPath, self).__init__(x, y, r, g, b)

		self.drawn = False
		self.pauseFirst = True
		self.pauseLast = True

		self.coords = coords

		self.theta = 0
		self.thetaRate = 0
		self.scale = 1.0
		self.scaleX = None
		self.scaleY = None
		self.jitter = True

		self.drawEvery = 1
		self.drawIndex = 1

		self.skip = 0

		self.flipX = False
		self.flipY = False

	def produce(self):
		"""
		Generate the points of the circle.
		"""
		r, g, b = (0, 0, 0)

		# Obect skipping algo
		self.drawIndex = (self.drawIndex+1) % self.drawEvery

		doDraw = True
		if not self.drawIndex in [0, 1]:
			doDraw = False

		if not doDraw:
			self.drawn = True
			return

		i = 0
		for c in self.coords:
			if self.jitter and random.randint(0, 2) == 0:
				continue

			if self.skip:
				i += 1
				if i % self.skip == 0:
					continue

			# Scale
			x = c['x'] * self.scale
			y = c['y'] * self.scale

			# Dimension independant scales
			if self.scaleX:
				x *= self.scaleX

			if self.scaleY:
				y *= self.scaleY

			# Rotate
			xx = x
			yy = y
			x = xx*math.cos(self.theta) - \
					yy*math.sin(self.theta)
			y = yy*math.cos(self.theta) + \
					xx*math.sin(self.theta)

			# Flip
			if self.flipX:
				x *= -1

			if self.flipY:
				y *= -1

			# Translate
			x += self.x
			y += self.y

			yield(int(x), int(y), self.r, self.g, self.b)

		self.drawn = True

