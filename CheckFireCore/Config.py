from os import getcwd, environ as ShellEnviron
import subprocess
import copy

class Config:
    def __init__(self, name, dict = {}):
        self.name = name
        self.escript = ""
        self.dscript = ""
        self.require = []
        self.description = ""
        self.rparams = []
        self.cparams = {}

        if dict != {}:
            self.escript = copy.deepcopy(dict["escript"])
            self.dscript = copy.deepcopy(dict["dscript"])
            self.require = copy.deepcopy(dict["require"])
            self.description = copy.deepcopy(dict["description"])
            self.rparams = copy.deepcopy(dict["rparams"])
            self.cparams = copy.deepcopy(dict["cparams"])

    def toDict(self):
        dict = {}
        dict["name"] = copy.deepcopy(self.name)
        dict["escript"] = copy.deepcopy(self.escript)
        dict["dscript"] = copy.deepcopy(self.dscript)
        dict["require"] = copy.deepcopy(self.require)
        dict["description"] = copy.deepcopy(self.description)
        dict["rparams"] = copy.deepcopy(self.rparams)
        dict["cparams"] = copy.deepcopy(self.cparams)

        return dict

    def getRequiredFiles(self):
        files = [self.escript, self.dscript]
        for i in self.require:
            files.append(i)
        return files

    def activate(self):
        for k,v in self.cparams.items():
            ShellEnviron[k] = v
        wd = getcwd() + "/temp/"
        subprocess.run(wd + self.escript, cwd=wd, stdout=subprocess.DEVNULL)

    def deactivate(self):
        for k,_ in self.cparams.items():
            if k in ShellEnviron:
                ShellEnviron.pop(k)
        wd = getcwd() + "/temp/"
        subprocess.run(wd + self.dscript, cwd=wd, stdout=subprocess.DEVNULL)

    def __str__(self):
        text = ""
        text += "Configuration {}\n".format(self.name)
        text += "{}\n".format(self.description)
        text += "Configuration params:\n"
        for k,v in self.cparams.items():
            text += "    {} = {}\n".format(k, v)
        text += "Enable script file: {}\n".format(self.escript)
        text += "Disable script file: {}\n".format(self.dscript)
        text += "Required params:\n"
        for i in self.rparams:
            text +=" {} ".format(i)
        text += "\n"
        text += "Files required: "
        for i in self.require:
            text += " {} ".format(i)
        text +="\n"

        return text