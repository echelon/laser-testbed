"""
PointStream -- The main galvo multiple object drawing
			   algorithm. This code is responsible for
			   drawing multiple objects. It will need to
			   be improved for efficiency.
"""

SHOW_TRACKING_PATH = False
SHOW_BLANKING_PATH = False
TRACKING_SAMPLE_PTS = 1
BLANKING_SAMPLE_PTS = 1

_CMAX = 65535 # MAX COLOR VALUE

import math
import random
import itertools
import sys
import threading
import time

class PointStream(object):
	def __init__(self):
		self.called = False
		self.stream = self.produce()

		# A list of all the objects to draw
		# XXX: For now, add and remove manually. 
		self.objects = []

		# A dictionary of objects registered using the new
		# addObject()/removeObject() API. This API has to 
		# be compatible with the existing API. 
		self.dictionary = {}
		self.dictIncrement = 0
		self.dictLock = threading.Lock()

		# Frame buffering
		self.nextFrame = []

		# Global object manipulation
		self.scale = 1.0
		self.rotate = 0.0
		self.translateX = 0
		self.translateY = 0

		# Tweakable parameters
		self.showTracking = SHOW_TRACKING_PATH
		self.showBlanking = SHOW_BLANKING_PATH
		self.trackingSamplePts = TRACKING_SAMPLE_PTS
		self.blankingSamplePts = BLANKING_SAMPLE_PTS

	def transform(self, point):
		"""
		Returns global SRT transformations on points.
		This isn't the most efficient way to do this
		since Python function calls are expensive, but
		I need this right now.

		This should be the last routine points pass
		through before being sent to the galvos.

		Point is a 5-tuple: (x, y, r, g, b)
		"""

		x = point[0]
		y = point[1]
		r = point[2]
		g = point[3]
		b = point[4]

		# Global Scale
		x = x * self.scale
		y = y * self.scale

		# Global Rotate
		# TODO
		xx = x
		yy = y
		x = xx*math.cos(self.rotate) - \
				yy*math.sin(self.rotate)
		y = yy*math.cos(self.rotate) + \
				xx*math.sin(self.rotate)

		# Global Translate
		x += self.translateX
		y += self.translateY

		return (int(x), int(y), r, g, b)

	def produce(self):
		"""
		This infinite loop functions as an infinite point
		generator. It generates points for objects as
		well as the "tracking" and "blanking" points
		that must occur between object draws.
		"""
		while True:
			#print "POINT STREAM LOOP BEGIN"
			curObj = None # XXX SCOPE HERE FOR DEBUG ONLY
			nextObj = None # XXX SCOPE HERE FOR DEBUG 
			reverse = False

			#self.requestLock()

			try:
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

				"""
				# TOPOLOGICAL SORT OF OBJECTS TO MAKE DRAWING
				# W/ GALVOS EFFICIENT!
				sortedObjects = []
				presort = objects[:]
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

				#sortedObjects = objects[:]
				objects = sortedObjects # XXX TURN OFF HERE
				"""

				# Draw all the objects... 
				for i in range(len(objects)):
					curObj = objects[i]
					nextObj = objects[(i+1)%len(objects)]

					# Skip draw?
					if curObj.skipDraw:
						continue

					# "DrawEvery" heuristic
					"""
					if hasattr(curObj, 'drawEveryHeuristic') and \
						curObj.drawEveryHeuristic:
							h = curObj
							h.drawEveryCount += 1
							if h.drawEveryCount % h.drawEvery != 0:
								continue
					"""

					# Prepare to cull object if it is marked destroy
					# TODO: Move this outside of object. 
					# TODO: Not PointStream's job
					if curObj.destroy:
						destroy.append(i)

					# FIXME: This is done twice for all firstPts
					# Once here, twice for tracking to nextObj
					firstPt = self.transform(curObj.firstPt)

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
							lastPt = self.transform(pt)
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
					nextFirstPt = self.transform(nextObj.firstPt)
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

				self.advanceFrame()

			except Exception as e:
				import sys, traceback
				while True:
					print '\n---------------------'
					print 'PointStream Exception: %s' % e
					traceback.print_tb(sys.exc_info()[2])
					print "---------------------\n"

			finally:
				#self.releaseLock()
				pass

	def setNextFrame(self, objects):
		"""
		Sets the next frame of objects to be displayed.
		Once the current frame finishes, the next frame will be
		set (and held until a new one comes).
		"""
		self.nextFrame = objects

	def advanceFrame(self):
		if not self.nextFrame:
			return
		self.objects = []
		self.objects = self.nextFrame[:]

	def addObject(self, obj):
		#self.requestLock()

		key = self.dictIncrement
		self.dictionary[key] = obj
		self.dictIncrement += 1

		self.objects = self.dictionary.values()

		#self.releaseLock()
		return key

	def addObjects(self, objects):
		#self.requestLock()
		keys = []
		for obj in objects:
			key = self.dictIncrement
			self.dictionary[key] = obj
			self.dictIncrement += 1
			keys.append(key)

		self.objects = self.dictionary.values()
		#self.releaseLock()
		return keys

	def removeObject(self, key):
		if key not in self.dictionary:
			print "Key DNE in Stream! Key='%s'" % str(key)
			return

		#self.requestLock()

		obj = self.dictionary.pop(key)
		self.objects = self.dictionary.values()

		#self.releaseLock()

		return obj

	def removeObjects(self, keys):
		#self.requestLock()
		objects = []
		for key in keys:
			if key not in self.dictionary:
				print "Key DNE in Stream! Key='%s'" % str(key)
				continue
			obj = self.dictionary.pop(key)
			objects.append(obj)

		self.objects = self.dictionary.values()
		#self.releaseLock()

	def read(self, n):
		d = [self.stream.next() for i in xrange(n)]
		return d

	def requestLock(self):
		self.dictLock.acquire()
		#while self.dictLock:
		#	continue
		#self.dictLock = True

	def releaseLock(self):
		self.dictLock.release()
		#self.dictLock = False


