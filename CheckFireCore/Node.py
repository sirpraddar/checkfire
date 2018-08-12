import requests
from threading import Thread
import configparser
from requests import ConnectionError,HTTPError

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

    def __power(self, command):
        payload = {'token': self.__token}
        uri = self.__URIgen('power/' + command)
        req = _AsyncRequest(uri,payload,defCallback)

    def shutdown(self):
        self.__power('shutdown')

    def reboot(self):
        self.__power('reboot')


def defCallback(req):
    pass


def loadNodesFromConfig():
        nodes = []
        conf = configparser.ConfigParser()
        conf.read('master.conf')
        for name,configs in conf.items():
            nodes.append(Node(name,configs))

        return nodes


def shutdownAllNodes():
    nodes = loadNodesFromConfig()
    for n in nodes:
        n.shutdown()


def rebootAllNodes():
    nodes = loadNodesFromConfig()
    for n in nodes:
        n.reboot()


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
        try:
            req = requests.post(self.__uri,json=self.__data)
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
            self.returnCode = -2
        self.done = True
        self.__callback(self)