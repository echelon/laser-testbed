#!/usr/bin/env python

"""
Play all animations listed.
Started May 30, 2013
"""

# XXX: Security hazard. 
# Never use in serious environment
# Executes strings as processes!

import os
import sys
import time
import subprocess

class Play(object):
	def __init__(self, fn, seconds):
		pwd = os.path.dirname(os.path.realpath(__file__))
		self.filename = fn
		self.fullpath = os.path.join(pwd, fn)
		self.wait = seconds
		self.proc = None
	def execute(self):
		cmd = self.fullpath
		self.proc = subprocess.Popen(cmd, shell=False)
	def close(self):
		self.proc.terminate()
		#self.proc.kill()
		#print "process id", self.proc.pid
		#os.kill(self.proc.pid, 9)

scripts = [
	#Play('../opencv/laser_edges.py', 7),
	#Play('ball.py', 7),
	#Play('fireworks.py', 10),
	Play('random_lines.py', 15),
	#Play('sine_wave.py', 10),
	Play('spin_square.py', 10),
	#Play('flicker.py', 6),
	#Play('trail_random.py', 15),
	Play('../../client/main.py', 20),
	#Play('bouncing_shapes.py', 10),
]

def main():
	while True:
		try:
			for script in scripts:
				script.execute()
				time.sleep(script.wait)
				script.close()
				time.sleep(0.1)

		except KeyboardInterrupt:
			subprocess.Popen('killall python')
			sys.exit()

if __name__ == '__main__':
	main()

