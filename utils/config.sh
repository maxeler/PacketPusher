#!/bin/bash

THIS_SCRIPT=$BASH_SOURCE

if [ "$BASH_SOURCE" = "$0" ]
	then
		echo "This script must be sourced!"
		exit 1
fi


MAXPROJUTILS=`dirname $THIS_SCRIPT`

export MAXPROJUTILS=`readlink -e $MAXPROJUTILS`

echo Setting MAXPROJUTILS to $MAXPROJUTILS

export PYTHONPATH="$MAXPROJUTILS/build:$PYTHONPATH"
