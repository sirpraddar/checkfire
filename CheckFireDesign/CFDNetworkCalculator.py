import re
import ipaddress


class NetworkCalculator():
    def __init__(self, network):
        self.hosts = {}
        self.networks = {}
        self.groups = {}

        for k,v in network.items():
            if re.match("Net:\w+",k):
                if re.match('^([0-9]{1,3}\.){3}[0-9]{1,3}$',v['Address']) and 'Netmask' in v.keys():
                    v['Address'] = str(ipaddress.ip_network(v['Address'] + '/' + v['Netmask']))

                self.networks[k[4:]] = v

            try:
                for h in v["Host"].split():
                    hh = re.split('[=:]',h)
                    self.hosts[hh[0]] = hh[1]
            except KeyError:
                pass
            try:
                for g in v["Groups"].split():
                    gg = re.split("[=:]",g)
                    self.groups[gg[0]] = gg[1]
            except KeyError:
                pass

    def resolveDestAddress(self,name):
        try:
            return self.hosts[name]
        except KeyError:
            pass
        try:
            return self.networks[name]["DestNode"]
        except KeyError:
            pass
        try:
            return self.groups[name]
        except KeyError:
            pass

        raise KeyError

    def getNetworkNode(self, netName):
        return self.networks[netName]["SourceNode"]

    def getWorkerNode(self,string):
        if re.match('([0-9]{1,3}\.){3}[0-9]{1,3}\-[0-9]{1,3}',string):
            add, _  = string.split('-')
        elif re.match('([0-9]{1,3}\.){3}[0-9]{1,3}',string):
            add = string
        else:
            try:
                add = self.hosts[string]

            except KeyError:
                return self.networks[string]["SourceNode"].split(',')[0]

        for _ , n in self.networks.items():
            net = ipaddress.ip_network(n["Address"])
            if ipaddress.ip_address(add) in net.hosts():
                for node in n["SourceNode"].split(','):
                    if node == string:
                        return node

                return n["SourceNode"].split(',')[0]
            elif n['SourceNode'] == string:
                return string
    @staticmethod
    def getNetworkRangeAddresses (address):
        #Check if it is a network address
        if re.match("([0-9]{1,3}\.){3}[0-9]{1,3}\/[0-9]{1,2}",address):
            net = ipaddress.ip_network(address)
            return net[0] , net[-1]
        return None