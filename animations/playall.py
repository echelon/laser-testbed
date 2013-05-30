#!/usr/bin/env python

"""
Play all animations listed.
Started May 30, 2013
"""

# XXX: Security hazard. 
# Never use in serious environment
# Executes strings as processes!

import sys
import time
import subprocess

class Play(object):
	def __init__(self, fn, seconds):
		self.filename = fn
		self.wait = seconds
		self.proc = None
	def execute(self):
		cmd = './%s' % self.filename
		self.proc = subprocess.Popen(cmd, shell=False)
	def close(self):
		#self.proc.kill()
		self.proc.terminate()

scripts = [
	Play('ball.py', 7),
	Play('fireworks.py', 15),
	Play('sine_wave.py', 10),
	Play('spin_square.py', 6),
	Play('flicker.py', 6),
	Play('trail_random.py', 20),
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

