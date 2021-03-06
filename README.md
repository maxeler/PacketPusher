# PacketPusher

This is a simple state machine that aims to reproduce some of the functionality of the tcpreplay tool.  It takes in a pcap file and replays each packet in the file over an Ethernet port at the same rate at which they were originally captured, or optionally at a fixed rate.  It can achieve near-line rate speeds.


## How to build


### Bitstream

Before you start, the following two commands must be run:

    source ./utils/config.sh
    source ./utils/maxenv.sh

To build the MaxJ class files:

    cd bitstream
    ant

After the class files have been built, you can produce a simulation maxfile:

    ant sim

You can also compile for hardware **(this takes about 50 minutes)** with:

    ant dfe

After compiling your maxfile, copy it from the location given in the compiler output to the runtime directory:

    cp <maxfile location> ../runtime


### Runtime

Again, these two commands must have been run first:

    source ./utils/config.sh
    source ./utils/maxenv.sh

You can then compile the runtime code with:

    cd runtime
    ./build.py

This will produce an executable named "packetpusher" in the runtime directory.

## How to run

In the general case, replay is started by running the packetpusher executable with one mandatory argument and one optional one.

The runtime will wait for a key to be pressed before it unloads the maxfile and terminates.  This is to work around problems in the simulator with incomplete data being sent if the maxfile is unloaded immediately.

To replay each packet in a pcap file at the relative time at which it was captured:

    ./packetpusher example.pcap

You can also replay packets with a constant delay period, expressed in nanoseconds.  For example, to replay one packet per second:

    ./packetpusher example.pcap 1000000000

To replay packets as fast as possible (equivalent to tcpreplay's "-t" option):

    ./packetpusher example.pcap 0

Note that there may be a delay in processing large pcap files.  For speed, every pcap file is loaded into memory before replay begins, so you must make sure you have enough RAM.

'Old format' pcap files, with the timestamps in microseconds rather than nanoseconds, are not supported.  This program also will not work with files generated by tshark or wireshark, which use an extended format.

### Running in simulation

To start the simulator with the network settings configured appropriately, type (from the runtime directory):

    ./build.py start_sim

You will then need to set up the environment variables if you have not run the simulator before:

    export MAXELEROSDIR=$MAXCOMPILERDIR/lib/maxeleros-sim
    export LD_PRELOAD=$MAXELEROSDIR/lib/libmaxeleros.so:$LD_PRELOAD
    export SLIC_CONF="$SLIC_CONF;use_simulation=mbazleySim"

Then, in another terminal (or in wireshark), you can listen to traffic on the interface "tap0" while you run packetpusher.

To stop the simulator, use:

    ./build.py stop_sim

