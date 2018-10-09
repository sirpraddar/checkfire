#!/bin/bash

if [ -z ${COUNT+x} ]; then COUNT=4; fi
if [ -z ${INTERVAL+x} ]; then INTERVAL=0.2; fi

ping -c $COUNT -i $INTERVAL $DESTIP
