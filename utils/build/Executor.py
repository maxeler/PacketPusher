#!/usr/bin/env python

import socket
import subprocess
import os
import time
import datetime
import sys

class Executor(object):
	def __init__(self, logfile_path=None, append=False, logPrefix=None):
		self.process = None
		if (logfile_path):
			self.logfile = open(logfile_path, "a" if append else "w" )
			self.logfile_path = os.path.abspath(logfile_path)
		else:
			self.logfile = sys.stdout
			self.logfile_path = "stdout"

		self.logPrefix = logPrefix

	def getLogfilePath(self):
		return self.logfile_path

	def execCommand(self, params, wait_completion=0):
		self.log("Executing: %s" % ( " ".join(params) ))
		try:
			self.process = subprocess.Popen(params, stdout=self.logfile, stderr=self.logfile)
		except OSError, e:
			self.log("Failed to execute: %s" % (str(e)))
			sys.exit(1)

		if (wait_completion < 0):
			self.process.wait()
		elif (wait_completion > 0):
			while self.isRunning():
				time.sleep(1)
				wait_completion -= 1
				if (wait_completion == 0):
					self.log("\n[Executor] Process Timed-out")
					self.kill()
					return 1
					break
		return 0

	def writeToLog(self, what):
		self.logfile.write(what)

	def wait(self):
		self.process.wait()

	def kill(self):
		if self.isRunning():
			self.log("\n[Executor] Killing " + str(self.process.pid))
			self.process.kill()
			self.process.wait()

	def isRunning(self):
		if self.process is not None:
			return self.process.poll() is None
		return False

	def isSuccess(self):
		if self.process.returncode is not None:
			return self.process.returncode == 0
		return False

	def log(self, args):
		prefix = "" #datetime.datetime.utcnow().strftime("[%Y-%m-%d %H:%M:%S.%f] ")
		if self.logPrefix:
			prefix += self.logPrefix  
		self.logfile.write(prefix + args + "\n")
		self.logfile.flush()


