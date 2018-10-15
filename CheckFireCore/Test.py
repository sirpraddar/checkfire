from os import environ as ShellEnviron, getcwd
import subprocess
import copy
import ipaddress
import netaddr
from .CoreUtils import execShellCommand
from .GlobalSettings import TEMP_PATH

class Test:
    def __init__(self, dictLoaded={}, name=''):
        self.name = name
        self.description = ''
        self.script = ''
        self.configs = []
        self.require = []
        self.tparams = {}
        self.negate = False
        self.iploop = None

        if dictLoaded != {}:
            #self.name = name
            self.description = copy.deepcopy(dictLoaded["description"])
            self.script = copy.deepcopy(dictLoaded["script"])
            self.configs = copy.deepcopy(dictLoaded["configs"])
            self.require = copy.deepcopy(dictLoaded["require"])
            self.tparams = copy.deepcopy(dictLoaded["tparams"])
            self.negate = copy.deepcopy(dictLoaded["negate"])
            try:
                self.iploop = copy.deepcopy(dictLoaded["iploop"])
            except KeyError:
                pass

    def __str__(self):
        text = ""
        text += "Test {}\n".format(self.name)
        text += "{}\n".format(self.description)
        text += "Script file: {}\n".format(self.script)
        text += "Test Params:\n"
        for i,j in self.tparams.items():
            text +="    {} = {}\n".format(i,j)
        text += "\nConfigs required: "
        for i in self.configs:
            text += " {} ".format(i)
        text += "\n"
        text += "Files required: "
        for i in self.require:
            text += " {} ".format(i)
        text +="\n"
        if self.iploop:
            text += "LOOP FROM {} TO {}\n".format(self.iploop[0],self.iploop[1])
        if self.negate:
            text += "NEGATE ACTIVE\n"

        return text


    def toDict(self):
        dict = {}
        dict["name"] = copy.deepcopy(self.name)
        dict["description"] = copy.deepcopy(self.description)
        dict["script"] = copy.deepcopy(self.script)
        dict["configs"] = copy.deepcopy(self.configs)
        dict["require"] = copy.deepcopy(self.require)
        dict["tparams"] = copy.deepcopy(self.tparams)
        dict["negate"] = copy.deepcopy(self.negate)
        dict["iploop"] = copy.deepcopy(self.iploop)

        return dict

    def getRequiredFiles(self):
        files = []
        files.append(self.script)
        files.extend(self.require)
        return files

    def execTest(self):
        if self.iploop:
            return self.__execLoopTest()
        else:
            return self.__execTest()

    def __execLoopTest(self):
        iface, _ = execShellCommand('ip link show | grep -o -E "2: [a-z0-9]+" | grep -o -E "[a-z].[a-z0-9]+"')
        out ,  _ = execShellCommand('ip -4 address show ' + iface + ' | grep -o -m 1 -E "([0-9]+\.){3}[0-9]{1,3}\/?[1-9]?[0-9]?" | head -n1')
        out = out.split('/')
        backupIp = out[0]
        netmask = out[1]
        backupDefaultGW, _ = execShellCommand('ip route show | grep default | grep -o -E "([0-9]+\.){3}[0-9]+"')
        currentMAC , _ = execShellCommand('ip link | grep -A 1 ' + iface + ' | grep -E -o "([0-9a-f]{1,2}:){5}[0-9a-f]{1,2}" | head -n1')
        currentMAC = netaddr.EUI(currentMAC)
        iplow = ipaddress.ip_address(self.iploop[0])
        iphigh = ipaddress.ip_address(self.iploop[1])
        finalResult = 0
        finalText = ""

        while iplow <= iphigh:
            execShellCommand("ip link set " + iface + " interface down")
            execShellCommand("ip link set " + iface + " interface address " + str(netaddr.EUI(int(currentMAC) + int(iphigh) - int(iplow))))
            execShellCommand("ip link set " + iface + " interface up")

            execShellCommand('ip address flush dev {}'.format(iface))
            execShellCommand('ip address add {}/{} dev {}'.format(iplow,netmask,iface))
            execShellCommand('ip route add default via {}'.format(backupDefaultGW))

            errCode, result = self.__execTest()

            #execShellCommand('ip address delete {}/{} dev {}'.format(iplow, netmask, iface))

            if not errCode == 0:
                finalText += "Test failed for {}\n".format(iplow)
                finalText += result + "\n"
                finalText += '-------------------------------------------------------\n'

            finalResult += errCode
            iplow += 1

        execShellCommand("ip link set " + iface + " interface down")
        execShellCommand("ip link set " + iface + " interface address " + str(currentMAC))
        execShellCommand("ip link set " + iface + " interface up")

        execShellCommand('ip address flush dev {}'.format(iface))
        execShellCommand('ip address add {}/{} dev {}'.format(backupIp,netmask,iface))
        execShellCommand('ip route add default via {}'.format(backupDefaultGW))

        return finalResult, finalText

    def __execTest(self):
        wd = TEMP_PATH


        for k,p in self.tparams.items():
            ShellEnviron[k] = p

        #Exec test script
        result = subprocess.run(wd+self.script,cwd=wd,stdout=subprocess.PIPE)

        for k,_ in self.tparams.items():
            if k in ShellEnviron:
                ShellEnviron.pop(k)

        if self.negate:
            result.returncode = 127 if result.returncode == 0 else 0

        return (result.returncode, result.stdout.decode("ascii"))
