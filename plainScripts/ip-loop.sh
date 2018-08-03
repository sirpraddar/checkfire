#!/usr/bin/env bash

#Variables:
#  RANGE:   Specify IPs to loop for in bash form
#  NETMASK: Subnet mask
#  TEST:    Test to execute for each ip
#  IFACE:   Network interface to change
#  IPNAME:  Variable name for the ips in the subscript

if [ -z ${RANGE+x} ]; then
    echo "Missing RANGE parameter"
    exit 1
fi

if [ -z ${NETMASK+x} ]; then
    echo "Missing NETMASK parameter"
    exit 1
fi

if [ -z ${TEST+x} ]; then
    echo "Missing TEST parameter"
    exit 1
fi

if [ -z ${IPNAME+x} ]; then
    echo "Missing IPNAME parameter"
    exit 1
fi

if [ -z ${IFACE+x} ]; then
    IFACE=$(ls /sys/class/net/ | grep -v 'lo\|tun' | head - -n 1)
fi

SUCCESS=0;
BACKUP=$(ip -4 address show $IFACE | grep -o -m 1 -E "([0-9]+\.){3}[0-9]+" | head -n1)

for i in $(eval echo $RANGE); do

  if [ $(id -u) -eq 0 ]; then
    ip address flush dev $IFACE;
    ip address add $i/$NETMASK dev $IFACE;
  else
    sudo ip address flush dev $IFACE;
    sudo ip address add $i/$NETMASK dev $IFACE;
  fi

  export "${IPNAME}"="$i";

  RESULT=$(./$TEST)
  EXITCODE=$?
  if [ $EXITCODE -ne 0 ]; then
    echo "Test failed for $i:"
    echo $RESULT
    echo "---------------------------------"
    SUCCESS=$(expr $SUCCESS + $EXITCODE)
  fi
done

if [ $(id -u) -eq 0 ]; then
    ip address flush dev $IFACE;
    ip address add $BACKUP/$NETMASK dev $IFACE;
else
    sudo ip address flush dev $IFACE;
    sudo ip address add $BACKUP/$NETMASK dev $IFACE;
fi

exit $SUCCESS