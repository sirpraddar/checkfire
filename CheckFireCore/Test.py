from os import environ as ShellEnviron, getcwd
import subprocess
import copy
import platform, re


class Test:
    def __init__(self, dictLoaded={}, name=''):
        self.name = name
        self.description = ''
        self.script = ''
        self.configs = []
        self.require = []
        self.tparams = {}
        self.negate = False

        if dictLoaded != {}:
            #self.name = name
            self.description = copy.deepcopy(dictLoaded["description"])
            self.script = copy.deepcopy(dictLoaded["script"])
            self.configs = copy.deepcopy(dictLoaded["configs"])
            self.require = copy.deepcopy(dictLoaded["require"])
            self.tparams = copy.deepcopy(dictLoaded["tparams"])
            self.negate = copy.deepcopy(dictLoaded["negate"])

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

        return dict

    def getRequiredFiles(self):
        files = []
        files.append(self.script)
        files.extend(self.require)
        return files

    @property
    def execTest(self):
        wd = getcwd()
        for k,p in self.tparams.items():
            ShellEnviron[k] = p

        if platform.system() == "Windows":
            wd = wd + "\\temp\\"
            #script = "start " + self.script
            #script = "start " + wd + self.script
            winShells = {"ps1": "powershell.exe", "bat": "cmd.exe", "cmd": "cmd.exe"}
            extension = re.search('\.[\w\d]{3}$', self.script)
            extension = extension.group(0)
            extension = extension.lstrip('.')
            script = winShells.get(extension) + " " + wd + self.script
        # Exec test script
        else:
            wd = wd + "/temp/"
            script = wd + self.script
        result = subprocess.run(script,cwd=wd,stdout=subprocess.PIPE)

        for k,_ in self.tparams.items():
            if k in ShellEnviron:
                ShellEnviron.pop(k)

        if self.negate:
            result.returncode = 127 if result.returncode == 0 else 0

        return result.returncode, result.stdout.decode("ascii",errors="ignore")
