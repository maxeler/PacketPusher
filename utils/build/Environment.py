import os
import sys


def require(key):
	if not key in os.environ:
		print "Required environment variable not set: %s" % (key)
		sys.exit(1)
	val = os.environ.get(key)
	print "Required Environment variable: %s = %s" % (key, val)
	return val


def optional(key):
	if not key in os.environ:
		print "Optional environment variable not set: %s" % (key)
		return ""
	
	val = os.environ.get(key)
	print "Optional Environment variable: %s = %s" % (key, val)
	return val 


def set(key, value):
	if value:
		print "Setting environment %s <-- %s" % (key, value)
		os.environ[key] = value
	else:
		print "Unsetting environment variable %s" % (key)
		del os.environ[key]

