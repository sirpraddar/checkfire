import requests
from threading import Thread
import configparser


class Node:
    def __init__(self, name, configs=None):
        self.name = name
        if not configs:
            conf = configparser.ConfigParser()
            conf.read('master.conf')
        else:
            conf = configs
        self.__token = conf[name]['Token']
        self.__port = conf[name]['Port']
        self.__address = conf[name]['Address']
        self.results = None

    def execPackage (self,package):
        payload = {'token': self.__token,
                   'data': package.toDict()}
        uri = 'http://' + self.__address + ':' + self.__port + '/execute'
        req = _AsyncRequest(uri,payload,self.callback)
        req.start()

    def callback(self, req):
        self.results = req.results

    def loadPackage (self,package):
        pass



def defCallback(req):
    pass


class _AsyncRequest(Thread):
    def __init__(self,uri,data,callback=defCallback):
        Thread.__init__(self)
        self.__uri = uri
        self.__data = data
        self.results = None
        self.done = False
        self.returnCode = 0
        self.__callback = callback

    def run(self):
        req = requests.post(self.__uri,json=self.__data)
        self.results = req.json()
        self.done = True
        self.returnCode = req.status_code
        self.__callback(self)