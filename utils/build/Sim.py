#!/usr/bin/env python

import os
import sys
import getpass

try:
	import Environment
	from Executor import *
except ImportError, e:
	print "Couldn't find project-utils modules."
	sys.exit(1)


network_config = [ 
				{ 'NAME' : 'QSFP_TOP_10G_PORT0', 'DFE': '172.16.50.1', 'TAP': '172.16.50.10', 'NETMASK' : '255.255.255.0' }, 
				{ 'NAME' : 'QSFP_BOT_10G_PORT0', 'DFE': '172.16.60.1', 'TAP': '172.16.60.10', 'NETMASK' : '255.255.255.0' }
			] 

class MaxCompilerSim(Executor):
	def __init__(self, dfeModel):
		super(MaxCompilerSim, self).__init__(logPrefix="[MaxCompilerSim] ")
		self.MAXCOMPILERDIR = Environment.require("MAXCOMPILERDIR")
		self.dfeModel = dfeModel
		self.ORIG_MAXELEROSDIR = Environment.optional("MAXELEROSDIR")
		self.ORIG_LD_PRELOAD = Environment.optional("LD_PRELOAD")
		self.ORIG_SLIC_CONF = Environment.optional("SLIC_CONF")
		self.envSet = False

	def getSimName(self):
		return getpass.getuser() + 'Sim'

	def getSimDeviceName(self):
		return '%s0:%s' % (self.getSimName(), self.getSimName())

	def getSimNameParam(self):
		return ['-n', self.getSimName()] 

	def getMaxCompilerSim(self):
		return ['%s/bin/maxcompilersim' % self.MAXCOMPILERDIR]

	def getDfeModelParam(self):
		return ['-c', self.dfeModel]

	def getNetSimParams(self, config):
		params = [] 
		for p in config:
			params += ['-e', p['NAME'] + ':%s:%s' % (p['TAP'], p['NETMASK'])]
			params += ['-p', p['NAME'] + ':%s.pcap' % (p['NAME'])]
		return params
	
	def getSimBaseParams(self):
		return self.getMaxCompilerSim() + self.getSimNameParam()

	def getSimParams(self, netConfig):
		return self.getSimBaseParams() + self.getDfeModelParam() + self.getNetSimParams(netConfig)

	def start(self, netConfig=network_config):
		if self.isRunning():
			print "Cannot start another instance of the simulator. Please stop the previous one."
			return 
		self.execCommand(self.getSimParams(netConfig) + ["restart"])	
		self.wait()
		self.setSimEnv()

	def stop(self):
		self.execCommand(self.getSimBaseParams() + ["stop"] )
		self.wait()
		self.revertSimEnv()

	def setSimEnv(self):
		if not self.envSet:
			print "Setting Simulation Environment..."
			maxelerosdir = self.MAXCOMPILERDIR + "/lib/maxeleros-sim"
			Environment.set("MAXELEROSDIR", maxelerosdir)
			Environment.set("LD_PRELOAD", maxelerosdir + "/lib/libmaxeleros.so:" + self.ORIG_LD_PRELOAD)
			Environment.set("SLIC_CONF", self.ORIG_SLIC_CONF + "use_simulation=" + self.getSimName())
			self.envSet = True
	
	def revertSimEnv(self):
		if self.envSet:
			print "Reverting Simulation Environment..."
			Environment.set("MAXELEROSDIR", self.ORIG_MAXELEROSDIR)
			Environment.set("LD_PRELOAD", self.ORIG_LD_PRELOAD)
			Environment.set("SLIC_CONF", self.ORIG_SLIC_CONF)
			self.envSet = False

	def maxdebug(self, maxfiles):
		self.setSimEnv()
		for m in maxfiles:
			self.execCommand(['maxdebug', '-g', 'graph_%s' % self.getSimName(), '-d',  self.getSimDeviceName(), m])
		self.wait()

