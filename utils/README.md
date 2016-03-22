# Project Utils

A collection of useful tools / scripts for Maxeler Projects

## Environment

1. config.sh - configures the MAXPROJUTILS and PYTHONPATH environment variables
2. maxenv.sh - invokes maxenv.py to try and configure useful environment variables

## Scrtips

These are python modules which should help in compiling and running the simulation runtime easier

1. RuntimeBuilder.py - This helps with compiling and linking of source and .max files 
2. Sim.py - This helps with maxcompilersim
3. Executor.py - A wrapper script for executing binaries (includes: wait, kill, log etc.)

## Example

```python
MAXFILES = ['MyProject.max']
sources = ['myproject.c']
target = 'myproject'
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

def run_sim():
	build()
	s.start()
	e.execCommand([ "./" + target ])
	e.wait()
#	s.stop()
	

def maxdebug():
	s.maxdebug(MAXFILES)
```


