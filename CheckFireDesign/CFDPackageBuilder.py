import configparser
from CheckFireCore import TestPackage
from .CFDPolicyParser import PolicyParser

def readFile (path):
    cnf = configparser.ConfigParser(delimiters=('=',';'))
    cnf.optionxform = str
    cnf.read(path)
    return cnf

class PackageBuilder():
    def  __init__(self,networkFilePath,testLibH):
        self.cnfNetwork = readFile(networkFilePath)
        self.netName = self.cnfNetwork['NETWORK']['name']
        self.testlibpakdescr = readFile(testLibH)

    def buildPackage(self):
        pp = PolicyParser(self.testlibpakdescr)
        return pp.parseNetwork(self.cnfNetwork)


