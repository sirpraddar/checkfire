#!/usr/bin/env python

from CheckFireNode.CFNApp import CFNApp
import configparser
from CheckFireCore.GlobalSettings import *

if __name__ == '__main__':
    conf = configparser.ConfigParser()
    conf.read(NODE_CONF_PATH)
    address = conf['Socket']['Address']
    port = conf['Socket']['Port']

    CFNApp.run(address,port,debug=True)