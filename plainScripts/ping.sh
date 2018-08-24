#!/bin/bash

if [ -z ${COUNT+x} ]; then COUNT=4; fi
if [ -z ${TIMEOUT+x} ]; then TIMEOUT=1; fi

ping -c $COUNT -W $TIMEOUT $DESTIP
