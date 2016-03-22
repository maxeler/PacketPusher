import os
import sys

try:
	import fabricate
	import Environment
	import Executor
except ImportError, e:
	print "Couldn't find project-utils modules."
	sys.exit(1)


class MaxRuntimeBuilder(object):
	def __init__(self, maxfiles=[], cc='gcc'):
		self.MAXELEROSDIR = Environment.require("MAXELEROSDIR")
		self.MAXCOMPILERDIR = Environment.require("MAXCOMPILERDIR")
		self.MAXNETDIR = Environment.optional("MAXCOMPILERNETDIR")
		self.cc = cc
		self.maxfiles = maxfiles

	def verifyMaxfiles(self):
		for maxfile in self.maxfiles:
			if not os.path.isfile(maxfile):
				print "Maxfile doesn't exist: '%s'" % (maxfile)
				sys.exit(1)
			if not maxfile.endswith('.max'):
				print "Maxfile doesn't end with .max: '%s'" % (maxfile)
				sys.exit(1)

	def getMaxelerOsInc(self):
		"""return the include paths for MaxelerOS."""
		return ['-I%s/include' % self.MAXELEROSDIR]

	def getMaxelerOsLibs(self):
		"""Return the MaxelerOS libraries to be used in linking."""
		return ['-L%s/lib' % self.MAXELEROSDIR, '-lmaxeleros']

	def getSlicInc(self):
		"""Return the SLiC include paths."""
		return ['-I%s/include/slic' % self.MAXCOMPILERDIR]

	def getSlicLibs(self):
		"""Return the SLiC libraries to be used in linking."""
		return ['-L%s/lib' % self.MAXCOMPILERDIR, '-lslic']

	def getMaxNetInc(self):
		"""Return the include paths for Networking."""
		if not self.MAXNETDIR:
			return []
		return ['-I%s/include/slicnet' % self.MAXNETDIR]

	def getMaxNetLibs(self):
		"""Return the Networking libraries to be used in linking."""
		if not self.MAXNETDIR:
			return []
		return ['-L%s/lib' % self.MAXNETDIR, '-lslicnet']

	def getMaxfileLibs(self):
		"""Return the Maxfile object to be used in linking."""
		self.verifyMaxfiles()	
		return [maxfile.replace('.max', '.o') for maxfile in self.maxfiles]

	def getCompileFlags(self):
		"""Return all runtime include paths"""
		return self.getMaxelerOsInc() + self.getSlicInc() + self.getMaxNetInc()

	def getLinkFlags(self):
		"""Returns the libraries to be used for linking."""
		return self.getMaxfileLibs() + self.getMaxNetLibs() + self.getSlicLibs() + self.getMaxelerOsLibs() + ['-lpthread', '-lm', '-lrt'] 

	def slicCompile(self):
		"""Compile maxfiles in to a .o file"""
		self.verifyMaxfiles()	
		for m in self.maxfiles:
			fabricate.run("%s/bin/sliccompile" % (self.MAXCOMPILERDIR), m, m.replace('.max', '.o'))

	def compile(self, sources):
		for s in sources:
			fabricate.run(self.cc, self.getCompileFlags(), '-c', s, '-o', s.replace('.c', '.o'))

	def link(self, sources, target):
		objects = [s.replace('.c', '.o') for s in sources]
		fabricate.run(self.cc, objects, self.getLinkFlags(), '-o', target)

	def clean(self):
		fabricate.autoclean()



def main():
	fabricate.main()
