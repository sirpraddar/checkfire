#!/usr/bin/env python3

from CheckFireShell.CFShell import CFShell
import argparse

parser = argparse.ArgumentParser(description="Launches checkfire commands in cli mode.")
parser.add_argument('-p', '--package',nargs=1,help="Loads a package. Same as use command",action='store')
parser.add_argument('-t', '--test', nargs=1,help='Specify a test contained in package. Same as select command',action='store')
parser.add_argument('CMDLINE', nargs='+', help="Command to execute with arguments",action='append')

arguments = parser.parse_args()

shell = CFShell()
cmdline = arguments.CMDLINE[0]
#print (arguments)
if arguments.package is not None:
    shell.executeCommand(['use', arguments.package[0]])
if arguments.test is not None:
    shell.executeCommand(['select', arguments.test[0]])

shell.executeCommand(cmdline)
