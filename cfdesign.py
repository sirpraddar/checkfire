#!/usr/bin/env python

import argparse
import configparser
from CheckFireDesign.CFDPackageBuilder import PackageBuilder


argparser = argparse.ArgumentParser(description="Utility to auto build test packages using network configurations.")
argparser.add_argument('LIBRARY_HEADER_FILE',nargs=1,help="library header file path")
argparser.add_argument('NETWORK_FILE',nargs=1,help="network and policy specifications file path")
argparser.add_argument('--print-package',help="print constructed package info",action='store_true',dest='ppackage')
argparser.add_argument('--print-tests',help="print tests contained in constructed package",action='store_true',dest='ptests')

args = argparser.parse_args()

'''
network = configparser.ConfigParser(delimiters=('=',';'))
network.read(args.NETWORK_FILE[0])
libh = configparser.ConfigParser()
libh.read(args.LIBRARY_HEADER_FILE[0])
pp = PolicyParser(libh)
package = pp.parseNetwork(network)
'''
pb = PackageBuilder(args.NETWORK_FILE[0],args.LIBRARY_HEADER_FILE[0])
package = pb.buildPackage()

if args.ppackage:
    print(package)

if args.ptests:
    for n,t in package.tests.items():
        print(t)
