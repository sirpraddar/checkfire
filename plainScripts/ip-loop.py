#!/usr/bin/env python

'''
Variables needed to the script to be set:
#  IPLOW:   Start loop ip
#  IPHIGH:  End loop ip
#  NETMASK: Subnet mask
#  TEST:    Test script to execute for each ip
#  IFACE:   Network interface to change
#  IPNAME:  Variable name for the ips in the subscript
'''

import ipaddress
from os import getenv
import subprocess

iplow = getenv("IPLOW")
iphigh = getenv("IPHIGH")
netmask = getenv("NETMASK")
testscript = getenv("TEST")
iface = getenv("IFACE")

if not iplow:
    print ("Start ip not set.")
    exit(1)
if not iphigh:
    print ("End ip not set.")
    exit(1)
if not netmask:
    print ("netmask not set.")
    exit(1)
if not testscript:
    print ("Test script not set.")
    exit(1)

if not iface:
    proc = subprocess.Popen("ls /sys/class/net/ | grep -v 'lo\|tun' | head - -n 1", shell=True,stdout=subprocess.PIPE)
    iface = proc.stdout.read()
    iface = iface[:-1]

success = 0
proc = subprocess.Popen('ip -4 address show ' + iface + ' | grep -o -m 1 -E "([0-9]+\.){3}[0-9]+" | head -n1', shell=True, stdout=subprocess.PIPE)
backupIP = proc.stdout.read()
proc = subprocess.Popen('ip route show | grep default | grep -o -E "([0-9]+\.){3}[0-9]+"',shell=True,stdout=subprocess.PIPE)
backupDGW = proc.stdout.read()

iplow = ipaddress.ip_address(iplow)
iphigh = ipaddress.ip_address(iphigh)

finalCode = 0

while iplow <= iphigh:
    if ipcurr:
        subprocess.Popen('ip address delete {}/{} dev {}'.format(ipcurr,netmask,iface), shell=True).wait()
    ipcurr = iplow
    #subprocess.Popen('ip address flush dev {}'.format(iface),shell=True).wait()
    subprocess.Popen('ip address add {}/{} dev {}'.format(ipcurr,netmask,iface)).wait()
    subprocess.Popen('ip route add default via {}'.format(backupDGW))

    proc = subprocess.Popen(testscript,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    result = proc.stdout.read()
    errCode = proc.returncode

    if not errCode == 0:
        print("Test failed for {}".format(ipcurr))
        print(result)
        print ('-------------------------------------------------------')

    finalCode += errCode

    iplow += 1

subprocess.Popen('ip address flush dev {}'.format(iface),shell=True).wait()
subprocess.Popen('ip address add {}/{} dev {}'.format(backupIP,netmask,iface)).wait()
subprocess.Popen('ip route add default via {}'.format(backupDGW))

exit(finalCode)