import time
import thread
import random

from lib import dac
from lib.common import *
import fakedac

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
from lib.importObj import importObj


class Show(object):
	"""
	Laser Show
	This class controls the entire show and can switch
	between different animations (which have different
	backing code).
	"""
	def __init__(self):
		# Pointstream (prolly refactor)
		self.stream = None

		self.animations = []
		self.curIdx = 0
		self.isTimed = False

	# XXX: POOR DESIGN, UGH!
	def _switchBefore(self):
		anim = self.animations[self.curIdx]
		anim.stopAnimThread()

		# Remove all onscreen objects
		self.stream.objects = []

	def _switchAfter(self):
		anim = self.animations[self.curIdx]
		anim.notifyRestarted()
		anim.startAnimThread()

		# Add all objects to be drawn
		for obj in anim.objects:
			self.stream.objects.append(obj)

		# Switch stream parameters
		self.stream.blankingSamplePts = \
				anim.blankingSamplePts
		self.stream.trackingSamplePts = \
				anim.trackingSamplePts

	def next(self):
		self._switchBefore()
		self.curIdx = (self.curIdx+1) % \
						len(self.animations)
		self._switchAfter()

	def prev(self):
		self._switchBefore()
		self.curIdx = (self.curIdx-1) % \
						len(self.animations)
		self._switchAfter()

	def random(self):
		self._switchBefore()
		self.curIdx = random.randint(0,
						len(self.animations) - 1)
		self._switchAfter()

	def start_dac_thread(self):
		"""
		Start the DAC / PointStream thread.
		It is self-healing and should tolerate all kinds
		of errors.
		"""

		def t():
			# TODO: Reoptimize below.
			# TODO: Does this belong here?
			# TODO: Where does anything belong?
			while True:
				try:
					d = dac.DAC(dac.find_first_dac())
					d.play_stream(self.stream)

				except KeyboardInterrupt:
					sys.exit()

				except Exception as e:
					import sys, traceback
					print '\n---------------------'
					print 'DacThread Exception: %s' % e
					print '- - - - - - - - - - -'
					traceback.print_tb(sys.exc_info()[2])
					print "\n"

		thread.start_new_thread(t, ())

	def start_testdac_thread(self):
		"""
		This is just a test -- it'll just print points and
		never send to a laser projector.
		"""

		def t():
			# TODO: Reoptimize below.
			# TODO: Does this belong here?
			# TODO: Where does anything belong?
			while True:
				try:
					d = fakedac.Dac2()
					d.play_stream(self.stream)

				except KeyboardInterrupt:
					sys.exit()

				except Exception as e:
					import sys, traceback
					print '\n---------------------'
					print 'DacThread Exception: %s' % e
					print '- - - - - - - - - - -'
					traceback.print_tb(sys.exc_info()[2])
					print "\n"

		thread.start_new_thread(t, ())



	"""
	def getCurAnim(self):
		# TODO: This would manage the timer if
		# a timeout is currently set.
		return self.animations[self.curIdx]
	"""

class Animation(object):
	"""
	Animation

	This class controls the animation setup, thread
	spawing and shutdown, configuration, etc.
	"""

	# Scaling animations (defaults)
	SCALE_MAX = 1.75
	SCALE_MIN = 0.5
	SCALE_RATE = 0.1

	# Tilting animations - oscillating theta (defaults)
	TILT_THETA_MAX = 0.4
	TILT_THETA_MIN = -0.4
	TILT_THETA_RATE = 0.05

	def __init__(self):
		# Frames *OR* objects, I suppose? 
		# Figure it out later. Depends on what PointStr 
		# eventually does. Which will PS take? 
		self.frames = []
		self.objects = []
		self.curIdx = 0
		self.timeDelta = None
		self.timeLast = None

		self.hasAnimationThread = False
		self.animationSleep = 0.05
		self._doRunThread = True # To turn on/off

		self.blankingSamplePts = 12
		self.trackingSamplePts = 12

		self.setup()

	def setup(self):
		"""
		Performs the work of main() for the animation.
		This typically is used to parameterize, setup,
		spawn threads.
		"""
		pass

	def notifyRestarted(self):
		"""
		Let the animation know it has been restarted.
		This can be used to restart certain animations,
		etc.
		"""
		pass

	def animThreadFunc(self):
		"""
		Performs any animation processing in an independent
		thread. Override if necessary. See the relevant member
		vars for controlling.
		"""
		pass

	def startAnimThread(self):
		"""
		Launch Thread. (And thread def.)
		"""
		def t():
			self._doRunThread = True
			while self._doRunThread:
				self.animThreadFunc()
				time.sleep(self.animationSleep)

		if not self.hasAnimationThread:
			return

		thread.start_new_thread(t, ())

	def stopAnimThread(self):
		"""
		Exit Thread.
		"""
		self._doRunThread = False

class AdvancedAnimation(Animation):
	"""
	Easy Animation
	"""

	def __init__(self, loadFile, init = None, anim = None,
			r=CMAX, g=CMAX, b=CMAX):

		super(AdvancedAnimation, self).__init__()

		self.loadFilename = loadFile

		self.initParams = init
		self.animParams = anim

		self.r = r
		self.g = g
		self.b = b

		self.timeLast = datetime.now() # For timedelta

		self.scaleX = 1.0
		self.scaleY = 1.0
		self.scaleDirecX = True
		self.scaleDirecY = True

		self.rotate = 0.0
		self.rotateDirec = True

		self.loadFile()

	def loadFile(self):
		"""
		Do file loading.
		Override me!!
		"""
		# XXX: This kind of makes 'setup()' pointless
		pass

	def animThreadFunc(self):
		"""
		This does all the simple animation!
		Saves a ton of time writing custom animations.
		"""
		ap = self.animParams or {}

		if not self.timeLast:
			self.timeLast = datetime.now()

		last = self.timeLast
		now = datetime.now()

		delta = now - last
		delta = delta.microseconds / float(10**3)

		if 'scale' in ap and ap['scale']:
			scaleMinX = 0.0
			scaleMaxX = 0.0
			scaleMinY = 0.0
			scaleMaxY = 0.0
			scaleRateX = 0.0
			scaleRateY = 0.0

			# Specify dimensions together?
			# TODO: Extremely flexible assignment
			if 'scaleMin' in ap:
				scaleMinX = ap['scaleMin']
				scaleMinY = ap['scaleMin']
				scaleMaxX = ap['scaleMax']
				scaleMaxY = ap['scaleMax']

			else:
				scaleMinX = ap['scaleMinX']
				scaleMinY = ap['scaleMinY']
				scaleMaxX = ap['scaleMaxX']
				scaleMaxY = ap['scaleMaxY']

			if 'scaleRate' in ap:
				scaleRateX = ap['scaleRate']
				scaleRateY = ap['scaleRate']

			else:
				scaleRateX = ap['scaleRateX']
				scaleRateY = ap['scaleRateY']

			# Do scale animation

			scaleX = self.scaleX
			scaleY = self.scaleY

			if self.scaleDirecX:
				scaleX += scaleRateX * delta
			else:
				scaleX -= scaleRateX * delta

			if self.scaleDirecY:
				scaleY += scaleRateY * delta
			else:
				scaleY -= scaleRateY * delta

			if scaleX <= scaleMinX:
				scaleX = scaleMinX
				self.scaleDirecX = True
			elif scaleX >= scaleMaxX:
				scaleX = scaleMaxX
				self.scaleDirecX = False

			if scaleY <= scaleMinY:
				scaleY = scaleMinY
				self.scaleDirecY = True
			elif scaleY >= scaleMaxY:
				scaleY = scaleMaxY
				self.scaleDirecY = False

			self.scaleX = scaleX
			self.scaleY = scaleY

			for obj in self.objects:
				obj.scaleX = scaleX
				obj.scaleY = scaleY


		if 'rotate' in ap and ap['rotate']:
			rotate = self.rotate
			rotateRate = ap['rotateRate']
			rotateMax = 0.0
			rotateMin = 0.0
			rotateLimits = False

			if 'rotateMag' in ap:
				rotateLimits = True
				rotateMax = ap['rotateMag']
				rotateMin = -ap['rotateMag']
			elif 'rotateMin' in ap:
				rotateLimits = True
				rotateMax = ap['rotateMax']
				rotateMin = ap['rotateMin']

			if not rotateLimits:
				rotate += rotateRate * delta

			else:
				if self.rotateDirec:
					rotate += rotateRate * delta
				else:
					rotate -= rotateRate * delta

				if rotate <= rotateMin:
					rotate = rotateMin
					self.rotateDirec = True
				elif rotate >= rotateMax:
					rotate = rotateMax
					self.rotateDirec = False

			self.rotate = rotate

			for obj in self.objects:
				obj.theta = rotate

		if 'scale_x_mag' in ap:
			scaleX = self.scaleX
			if self.scaleDirecX:
				scaleX += ap['scale_x_rate'] * delta
			else:
				scaleX -= ap['scale_x_rate'] * delta

			if scaleX <= -ap['scale_x_mag']:
				scaleX = -ap['scale_x_mag']
				self.scaleDirecX = True

			elif scaleX >= ap['scale_x_mag']:
				scaleX = ap['scale_x_mag']
				self.scaleDirecX = False

			self.scaleX = scaleX

			for obj in self.objects:
				obj.scaleX = scaleX

		if 'scale_y_mag' in ap:
			scaleY = self.scaleY
			if self.scaleDirecY:
				scaleY += ap['scale_y_rate'] * delta
			else:
				scaleY -= ap['scale_y_rate'] * delta

			if scaleY <= -ap['scale_y_mag']:
				scaleY = -ap['scale_y_mag']
				self.scaleDirecY = True

			elif scaleY >= ap['scale_y_mag']:
				scaleY = ap['scale_y_mag']
				self.scaleDirecY = False

			self.scaleY = scaleY

			for obj in self.objects:
				obj.scaleY = scaleY

		self.timeLast = datetime.now()


