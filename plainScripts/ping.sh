#!/bin/bash

if [ -z ${COUNT+x} ]; then COUNT=4; fi
ping -c $COUNT $DESTIP
