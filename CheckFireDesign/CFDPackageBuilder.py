import configparser
from CheckFireCore import TestPackage
from .CFDPolicyParser import PolicyParser

def readFile (path):
    cnf = configparser.ConfigParser()
    cnf.read(path)
    return cnf

class PackageBuilder():
    def  __init__(self,networkFilePath,testLibH):
        self.cnfNetwork = readFile(networkFilePath)
        self.netName = self.cnfNetwork['DEFAULT']['name']
        self.testlibpakdescr = readFile(testLibH)
        self.policyParser = PolicyParser(self.testlibpakdescr)


    def buildPackage(self):
        pack = TestPackage()


