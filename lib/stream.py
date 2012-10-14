"""
PointStream -- The main galvo multiple object drawing algorithm.
			   This code is responsible for drawing multiple objects.
			   It will need to be improved for efficiency.

	FIXME/NOTE: The documentation / variable names are a bit out of date.
				"Ball", where it occurs, means "entity object".
"""

SHOW_TRACKING_PATH = False
SHOW_BLANKING_PATH = False
TRACKING_SAMPLE_PTS = 10
BLANKING_SAMPLE_PTS = 10

_CMAX = 65535 # MAX COLOR VALUE

import math
import random
import itertools
import sys
import thread
import time

class PointStream(object):
	def __init__(self):
		self.called = False
		self.stream = self.produce()

		# A list of all the objects to draw
		# XXX: For now, add and remove manually. 
		self.objects = []

		# Tweakable parameters
		self.showTracking = SHOW_TRACKING_PATH
		self.showBlanking = SHOW_BLANKING_PATH
		self.trackingSamplePts = TRACKING_SAMPLE_PTS
		self.blankingSamplePts = BLANKING_SAMPLE_PTS

	def produce(self):
		"""
		This infinite loop functions as an infinite point generator.
		It generates points for both balls as well as the "blanking"
		that must occur between them.
		"""
		while True:
			#print "POINT STREAM LOOP BEGIN"
			curObj = None # XXX SCOPE HERE FOR DEBUG ONLY
			nextObj = None # XXX SCOPE HERE FOR DEBUG ONLY

			try:

				# Generate and cache the first points of the objects.
				# Necessary in order to slow down galvo tracking as we
				# move to the next object. 

				for b in self.objects:
					b.cacheFirstPt()

				# Objects to destroy at end of loop
				destroy = []


				"""
				# TOPOLOGICAL SORT OF OBJECTS TO MAKE DRAWING W/
				# GALVOS EFFICIENT!
				sortedObjects = []
				presort = self.objects[:]
				sortedObjects.append(presort.pop(0))
				while len(presort):
					#lowx = presort[0].x
					lastObj = sortedObjects[-1]
					lowdist = 10000000
					li = 0
					for i in range(len(presort)):
						obj = presort[i]
						a = obj.x - lastObj.x
						b = obj.y - lastObj.y
						c = math.sqrt(a**2 + b**2)
						if c < lowdist:
							lowdist = c
							li = i
					sortedObjects.append(presort.pop(li))

				#sortedObjects = self.objects[:]
				self.objects = sortedObjects # XXX TURN OFF HERE
				"""

				# Draw all the objects... 
				for i in range(len(self.objects)):
					curObj = self.objects[i]
					nextObj = self.objects[(i+1)%len(self.objects)]

					# Skip draw?
					if curObj.skipDraw:
						continue

					# Prepare to cull object if it is marked destroy
					if curObj.destroy:
						destroy.append(i)

					# Blanking (on the way in), if set
					if curObj.doBlanking:
						p = curObj.firstPt
						p = (p[0], p[1], 0, 0, 0)
						# If we want to debug the blanking 
						if self.showBlanking:
							p = (p[0], p[1], _CMAX, 0, _CMAX)
						for x in range(self.blankingSamplePts):
							yield p

					# Draw the object
					lastPt = (0, 0, 0, 0, 0)
					if not curObj.drawn:
						yield curObj.firstPt # XXX: This was cached upfront!
						for x in curObj.produce():
							lastPt = x
							yield x

					"""
					# XXX: BULLET SPECIFIC -- Remove?
					if type(curObj) == Bullet:
						# Paint last pt for smoothness
						# XXX: Remove?
						for x in xrange(BLANK_SAMPLE_PTS):
							yield curObj.firstPt

						# Paint empty for smoothness
						# XXX: Remove?
						for x in xrange(BLANK_SAMPLE_PTS):
							yield (curObj.lastPt[0], curObj.lastPt[1],
									0, 0, 0)
					"""

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
					lastX = lastPt[0]
					lastY = lastPt[1]
					xDiff = lastPt[0] - nextObj.firstPt[0]
					yDiff = lastPt[1] - nextObj.firstPt[1]

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
				for b in self.objects:
					b.drawn = False

				# Items to destroy
				#print destroy
				destroy.sort()
				destroy.reverse()
				for i in destroy:
					self.objects.pop(i)

			except Exception as e:
				import sys, traceback
				while True:
					print '\n---------------------'
					print 'PointStream Exception: %s' % e
					traceback.print_tb(sys.exc_info()[2])
					print "---------------------\n"

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d


