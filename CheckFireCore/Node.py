from multiprocessing.synchronize import Lock

import requests
from threading import Thread
import configparser
from requests import ConnectionError,HTTPError
from json.decoder import JSONDecodeError
from threading import Condition

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

    def __URIgen(self,command):
        return 'http://' + self.__address + ':' + self.__port + '/' + command

    def execPackage (self,package):
        payload = {'token': self.__token,
                   'data': package.toDict()}
        uri = self.__URIgen('execute')
        req = _AsyncRequest(uri,payload,self.callback)
        req.start()

    def callback(self, req):
        self.results = req.results

    def loadPackage (self,package):
        pass

    def __generalRequest(self,command):
        payload = {'token': self.__token}
        uri = self.__URIgen(command)
        req = _AsyncRequest(uri, payload, defCallback)
        req.start()

    def __resultRequest(self,command,timeout=None):
        payload = {'token': self.__token}
        uri = self.__URIgen(command)
        return _SyncRequest(uri,payload,timeout).exec()

    def __power(self, command):
        self.__generalRequest('power/' + command)

    def shutdown(self):
        self.__power('shutdown')

    def reboot(self):
        self.__power('reboot')

    def update(self):
        self.__generalRequest('/admin/update')

    def ping(self):
        return self.__resultRequest('/ping',timeout=4)



def defCallback(req):
    pass


def loadNodesFromConfig():
        nodes = []
        conf = configparser.ConfigParser()
        conf.read('master.conf')
        for name in conf.sections():
            nodes.append(Node(name,conf))

        return nodes


def shutdownAllNodes():
    nodes = loadNodesFromConfig()
    for n in nodes:
        n.shutdown()


def rebootAllNodes():
    nodes = loadNodesFromConfig()
    for n in nodes:
        n.reboot()

def updateAllNodes():
    nodes = loadNodesFromConfig()
    for n in nodes:
        n.update()

def pingAllNodes():
    nodes = loadNodesFromConfig()
    res = {}
    for n in nodes:
        code, payload = n.ping()
        res[n.name] = code
    return res


class _AsyncRequest(Thread):
    def __init__(self,uri,data,callback=defCallback,timeout=3600):
        self.__uri = uri
        self.__data = data
        self.results = None
        self.done = False
        self.returnCode = 0
        self.__callback = callback
        self.__timeout = timeout
        Thread.__init__(self)

    def run(self):
        try:
            req = requests.post(self.__uri,json=self.__data,timeout=self.__timeout)
            self.results = req.json()
            self.returnCode = req.status_code
        except ConnectionError as ce:
            self.results = {
                "detailed" : "Connection Error with " + self.__uri,
                "brief" : {},
                "error" : -1
            }
            self.returnCode = -1
        except HTTPError as httpe:
            self.results = {
                "detailed": "Connection Error with " + self.__uri,
                "brief": {},
                "error": -2
            }
        except JSONDecodeError as jse:
            self.results = {
                "detailed": "Got empty or bad response from " + self.__uri,
                "brief": {},
                "error": -3
            }
            self.returnCode = -2
        self.done = True
        self.__callback(self)

class _SyncRequest():
    def __init__(self, uri, data, timeout=None):
        self.__uri = uri
        self.__data = data
        self.__lock = Condition()
        self.__timeout = timeout

    def exec(self):
        with self.__lock:
            req = _AsyncRequest(self.__uri,self.__data,self.callback,timeout=self.__timeout)
            req.start()
            while not req.done:
                self.__lock.wait()
        #When I'm here the request is ended
        return req.returnCode, req.results

    def callback(self,req):
        with self.__lock:
            self.__lock.notifyAll()