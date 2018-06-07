import requests
from threading import Thread
import configparser


class Node:
    def __init__(self, name):
        self.name = name
        conf = configparser.ConfigParser()
        conf.read('master.conf')
        self.__token = conf[name]['Token']
        self.__port = conf[name]['Port']
        self.__address = conf[name]['Address']
        self.__results = {}

    def execPackage (self,package):
        payload = {'token': self.__token,
                   'data': package.toDict()}
        uri = self.__address + ':' + self.__port + '/execute'
        req = _AsyncRequest(uri,payload)

    def loadPackage (self,package):
        pass

    def getResults(self):
        pass


def defCallback():
    pass


class _AsyncRequest(Thread):
    def __init__(self,uri,data,callback=defCallback):
        self.__uri = uri
        self.__data = data
        self.__results = {}
        self.done = False
        self.returnCode = 0
        self.__callback = callback

    def run(self):
        req = requests.post(self.__uri,json=self.__data)
        self.__results = req.json()
        self.done = True
        self.returnCode = req.status_code()
        self.__callback()

    def getResults(self):
        if self.done:
            return self.__results
        else:
            return None