"""
Gui tools to aid in developing the laser code.
"""

import gtk

gtk.gdk.threads_init()


""" 
=========================================================
				Primitives and Tools
=========================================================
"""

class Scale(gtk.HScale):
	"""
	Simple HScale creation.
	"""
	def __init__(self, lower=1, upper=11, val=1, step=0.10, page=1.0):
		"""
		Simplified constructor
		"""
		self.adj = gtk.Adjustment(value=val, lower=lower, upper=upper, 
									step_incr=step, page_incr=page, 
									page_size=1.0)

		super(gtk.HScale, self).__init__(adjustment=self.adj)

	def get_value(self):
		return self.adj.get_value()	

	def set_value(self, val):
		self.adj.set_value(val)

	def install_cb(self, fn, arg=None):
		"""Install callback"""
		self.adj.connect("value_changed", fn, self, arg)



class ScaleWithLabel(gtk.VBox):
	"""
	Scale with a textual label.
	"""
	def __init__(self, label="Untitled", lower=1, upper=11, val=1, 
			step=0.10, page=1.0):
		"""
		Simplified constructor.
		"""
		super(gtk.VBox, self).__init__()

		self.scale = Scale(lower=lower, upper=upper, val=val, 
							step=step, page=page)
		self.label = gtk.Label(label)

		self.pack_start(self.label, False, False, 0)
		self.pack_start(self.scale, False, False, 0)

	def get_value(self):
		return self.scale.get_value()	

	def set_value(self, val):
		self.scale.set_value(val)

	def install_cb(self, fn, arg=None):
		"""Install callback"""
		self.scale.adj.connect("value_changed", fn, self, arg)

""" 
=========================================================
					Actual GUIs 
=========================================================
"""

class BallGui(object):
	"""
	Gui for testing the two bouncing balls.
	"""

	def __init__(self):
		"""Build the window."""
	
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)

		def test(adj, widget):
			print "TEST FUNCTION"
			pass

		# Gui controls
		self.laserPowDenom = ScaleWithLabel("Laser Power Denominator", 1, 6, 
								val=3)
		self.samplePts = ScaleWithLabel(
						"Total Sample Points Per Circle", 40, 3000, 
						step=1, page=10, val=50)
		self.rotations = ScaleWithLabel("Rotations around each circle",
						1, 6, step=1, val=1)

		self.pauseStartPts = ScaleWithLabel("Pause Points @ Start",
						0, 200, val=8)
		self.pauseEndPts = ScaleWithLabel("Pause Points @ End",
						0, 200, val=8)
		self.blankPts = ScaleWithLabel("Blanking Points", 0, 100, step=1, 
							page=1, val=10)

		self.bounceVelMin = ScaleWithLabel("Bounce Velocity Min", 0, 5000, 
							step=1, page=10, val=75)
		self.bounceVelMax = ScaleWithLabel("Bounce Velocity Max", 0, 5000, 
							step=1, page=10, val=500)

		self.radiusA = ScaleWithLabel("Radius A", 100, 12000, 
							step=1, page=10, val=4000)
		self.radiusB = ScaleWithLabel("Radius B", 100, 12000, 
							step=1, page=10, val=8000)

		vbox = gtk.VBox()
		self.vbox = vbox

		vbox.pack_start(self.laserPowDenom, False, False, 0)
		vbox.pack_start(self.samplePts, False, False, 0)
		vbox.pack_start(self.rotations, False, False, 0)
		vbox.pack_start(self.pauseStartPts, False, False, 0)
		vbox.pack_start(self.pauseEndPts, False, False, 0)
		#vbox.pack_start(self.blankPts, False, False, 0)
		vbox.pack_start(self.bounceVelMin, False, False, 0)
		vbox.pack_start(self.bounceVelMax, False, False, 0)
		vbox.pack_start(self.radiusA, False, False, 0)
		vbox.pack_start(self.radiusB, False, False, 0)

		"""
		Circle A -- at the start, this will control BOTH
			* Sample Points
			* Rotations
			* Start Pause Points
			* End Pause Points

		Circle B
			* Sample Points
			* Rotations
			* Start Pause Points
			* End Pause Points

		Blanking
			* A -> B Sample Points
			* B -> A Sample Points
		"""


		"""
		box = gtk.VBox() 
		lab = gtk.Label("test")
		box.pack_start(lab, False, False, 0)
		box.pack_start(hscale, False, False, 0)
		"""

		# Add widgets.
		self.window.add(vbox)

		# Install event handlers.
		self.window.connect("delete_event", self.destroy)
		self.window.connect("destroy", self.destroy)

	def install_cb(self, fn):
		"""
		Install callback to catch everything that changes.
		We don't care enough to handle each scale widget independently. 
		"""
		for w in self.vbox:
			w.install_cb(fn, self)

	def main_loop(self):
		"""Turn over control to the GTK main loop."""
		self.window.show_all()
		gtk.main()

	def destroy(self, widget, data=None):
		"""Exit GTK main loop; finish program."""
		gtk.main_quit()

