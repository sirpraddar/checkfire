from os import environ as ShellEnviron, getcwd
import subprocess
import copy

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

    def execTest(self):
        wd = getcwd() + "/temp/"


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
