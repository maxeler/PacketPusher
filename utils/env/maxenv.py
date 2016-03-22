#!/usr/bin/env python

import os
import tempfile
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-c", "--maxcompiler", dest="maxcompiler",
				  help="Set MaxCompiler directory", action="store", type="string")

parser.add_option("-o", "--maxeleros", dest="maxeleros",
				  help="Set MaxelerOS directory", action="store", type="string")


parser.add_option("-n", "--maxnet", dest="maxnet",
				  help="Set MaxCompilerNet directory", action="store", type="string")

parser.add_option("-s", "--script", dest="script", default=False, action="store_true",
				  help="Generates a bash script and commands, useful when 'eval'ing the output in a script")

(options, args) = parser.parse_args()


maxenv = { "CHECKOUTROOT" : None, 
		   "MAXCOMPILERDIR" : None, 
		   "MAXCOMPILERJCP" : None, 
		   "MAXCOMPILERNETDIR" : None, 
		   "MAXCOMPILERNETJCP" : None, 
		   "MAXELEROSDIR" : None }

def isMaxCompilerDistribution(location):
	if os.path.isfile(location + "/lib/MaxCompiler.jar") and os.path.isdir(location + "/include/slic"):
		return True
	return False

def isMaxNetDistribution(location):
	if os.path.isfile(location + "/lib/MaxCompilerNet.jar") and os.path.isdir(location + "/include/slicnet"):
		return True
	return False

		
def isMaxelerOsRpmInstalled():
	if os.path.isdir("/opt/maxeler/maxeleros") and os.path.isfile("/opt/maxeler/maxeleros/lib/libmaxeleros.so"):
		return True
	return False

def isMaxelerOsDriverLoaded():
	if os.path.isdir("/proc/maxeler/dev0/"):
		return True
	return False

def isCheckout(location):
	if location:
		if os.path.isdir(location + "/maxeda") and os.path.isdir(location + "/slicinterface"):
			return True
	return False


def guessMaxCompiler(location):
	if not location:
		# Check MAXCOMPILERDIR env
		if "MAXCOMPILERDIR" in os.environ:
			guessMaxCompiler(os.environ["MAXCOMPILERDIR"])
	else:
		# Check if this points to a distribution
		if isMaxCompilerDistribution(location):
			maxenv["MAXCOMPILERDIR"] = location 
			maxenv["MAXCOMPILERJCP"] = location + "/lib/MaxCompiler.jar"
		# checks if it points to a checkout
		elif isCheckout(location): 
			# use checkout as JCP
			maxenv["CHECKOUTROOT"] = location
			maxenv["MAXCOMPILERJCP"] = location + "/maxeda/bin"
			# check if there is a built distribution
			if isMaxCompilerDistribution(location + "/distribution/MaxCompiler"):
				maxenv["MAXCOMPILERDIR"] = location + "/distribution/MaxCompiler"
		elif isCheckout(location + "/.."):
			guessMaxCompiler(location + "/..")
		else:
			guessMaxCompiler(maxenv["CHECKOUTROOT"])
			

def guessMaxelerOs(location):
	if not location:
		if isMaxelerOsRpmInstalled():
			guessMaxelerOs("/opt/maxeler/maxeleros")
		elif "MAXELEROSDIR" in os.environ:
			guessMaxelerOs(os.environ.get("MAXELEROSDIR"))
		elif maxenv["CHECKOUTROOT"]:
			guessMaxelerOs(maxenv["CHECKOUTROOT"])
	else:
		if os.path.isfile(location + "/lib/libmaxeleros.so"):
			# Points at proper distribution
			maxenv["MAXELEROSDIR"] = location
		elif os.path.isfile(location +"/maxeleros/lib/libmaxeleros.so"):
			# points at RPM install root or maxeleros checkout root
			maxenv["MAXELEROSDIR"] = location + "/maxeleros"
		elif os.path.isfile(location +"/maxeleros/maxeleros/lib/libmaxeleros.so"):
			# points at maxeda checkout
			maxenv["MAXELEROSDIR"] = location + "/maxeleros/maxeleros"
		elif os.path.isfile("../lib/libmaxeleros.so"):
			# common mistake
			maxenv["MAXELEROSDIR"] = location + "/../"

def guessMaxNet(location):
	if not location:
		if "MAXCOMPILERNETDIR" in os.environ:
			guessMaxNet(os.environ["MAXCOMPILERNETDIR"])
		elif maxenv["CHECKOUTROOT"]:
			guessMaxNet(maxenv["CHECKOUTROOT"])
	else:
		if isMaxNetDistribution(location):
			maxenv["MAXCOMPILERNETDIR"] = location
			maxenv["MAXCOMPILERNETJCP"] = location + "/lib/MaxCompilerNet.jar"
		if isMaxNetDistribution(location + "/MaxCompiler"):
			maxenv["MAXCOMPILERNETDIR"] = location + "/MaxCompiler"
			if os.path.isdir(location + "../maxeda/bin"):
				maxenv["MAXCOMPILERNETJCP"] = location + "../maxeda/bin"
			else:
				maxenv["MAXCOMPILERNETJCP"] = location + "/MaxCompiler/lib/MaxCompilerNet.jar"
		elif isMaxNetDistribution(location + "/networking/distribution/MaxCompiler"):
			maxenv["MAXCOMPILERNETDIR"] = location + "/networking/distribution/MaxCompiler"
			maxenv["MAXCOMPILERNETJCP"] = location + "/networking/maxeda/bin"
		elif isMaxNetDistribution(location + "/distribution/MaxCompiler"):
			maxenv["MAXCOMPILERNETDIR"] = location + "/distribution/MaxCompiler"
			maxenv["MAXCOMPILERNETJCP"] = location + "/maxeda/bin"


if isCheckout(options.maxcompiler):
	maxenv["CHECKOUTROOT"] = options.maxcompiler
elif isCheckout(options.maxeleros):
	maxenv["CHECKOUTROOT"] = options.maxeleros
elif isCheckout(options.maxnet):
	maxenv["CHECKOUTROOT"] = options.maxnet


guessMaxCompiler(options.maxcompiler)
guessMaxelerOs(options.maxeleros)
guessMaxNet(options.maxnet)


for e in maxenv:
	if e == "CHECKOUTROOT":
		continue
	if maxenv[e]:
		maxenv[e] = os.path.normpath(maxenv[e])
		if options.script:
			print "echo '%s <-- %s' ;" % (e, maxenv[e])
			print "export %s=\"%s\" ;" % (e, maxenv[e])
		else:
			print "export %s=%s" % (e, maxenv[e])

