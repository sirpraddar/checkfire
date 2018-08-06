from os import environ as ShellEnviron, getcwd
import subprocess


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
            self.description = dictLoaded["description"]
            self.script = dictLoaded["script"]
            self.configs = dictLoaded["configs"]
            self.require = dictLoaded["require"]
            self.tparams = dictLoaded["tparams"]
            self.negate = dictLoaded["negate"]

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
        dict["name"] = self.name
        dict["description"] = self.description
        dict["script"] = self.script
        dict["configs"] = self.configs
        dict["require"] = self.require
        dict["tparams"] = self.tparams
        dict["negate"] = self.negate

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
