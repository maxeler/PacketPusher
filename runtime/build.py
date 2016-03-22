#!/usr/bin/env python

import sys

try:
	from RuntimeBuilder import *
	from Sim import *
except ImportError, e:
	print "Couldn't find project-utils modules."
	sys.exit(1)

MAXFILES = ['PacketPusher.max']
sources = ['packetpusher.c']
target = 'packetpusher'
includes = []


b = MaxRuntimeBuilder(maxfiles=MAXFILES)
s = MaxCompilerSim(dfeModel="ISCA")
e = Executor(logPrefix="[%s] " % (target))

def build():
	compile()
	link()

def compile():
	b.slicCompile()
	b.compile(sources)

def link():
	b.link(sources, target)

def clean():
	b.clean()

def start_sim():
	s.start(netConfig=[{ 'NAME' : 'QSFP_BOT_10G_PORT1', 'TAP': '172.17.2.1', 'NETMASK' : '255.255.255.224' }])

def stop_sim():
	s.stop()

def restart_sim():
	s.start()

def run_sim(pcap):
	build()
	start_sim()
	e.execCommand([ "./" + target, pcap])
	e.wait()
#	stop_sim()
	

def maxdebug():
	s.maxdebug(MAXFILES)

if __name__ == '__main__':
	fabricate.main()
