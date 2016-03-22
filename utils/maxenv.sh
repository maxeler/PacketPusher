#!/bin/bash

THIS_SCRIPT=$BASH_SOURCE

if [ "$BASH_SOURCE" = "$0" ]
	then
		echo "This script must be sourced!"
		exit 1
fi


ENV_DIR=`dirname $THIS_SCRIPT`
eval `/usr/bin/env python ${ENV_DIR}/env/maxenv.py -s`

