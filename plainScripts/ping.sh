#!/bin/bash

if [ -z ${COUNT+x} ]; then COUNT=4; fi
if [ -z ${INTERVAL+x} ]; then INTERVAL=0.2; fi

#ping -c $COUNT -i $INTERVAL $DESTIP

CODE=0

for i in $(seq 1 $COUNT); do
    timeout --preserve-status --signal INT $INTERVAL ping -c 1 $DESTIP > /dev/null
    if [ $? -ne 0 ]; then
        echo "ping $i failed"
        CODE=$(expr $CODE + 1)
    fi
done
echo "Packets lost: $CODE"
exit $CODE