from os import getcwd, environ as ShellEnviron
import subprocess


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
            self.escript = dict["escript"]
            self.dscript = dict["dscript"]
            self.require = dict["require"]
            self.description = dict["description"]
            self.rparams = dict["rparams"]
            self.cparams = dict["cparams"]

    def toDict(self):
        dict = {}
        dict["name"] = self.name
        dict["escript"] = self.escript
        dict["dscript"] = self.dscript
        dict["require"] = self.require
        dict["description"] = self.description
        dict["rparams"] = self.rparams
        dict["cparams"] = self.cparams

        return dict


    def activate(self):
        for k,v in self.cparams.items():
            ShellEnviron[k] = v
        wd = getcwd() + "/temp/"
        subprocess.run(wd + self.escript, cwd=wd, stdout=subprocess.DEVNULL)

    def deactivate(self):
        for k,_ in self.cparams.items:
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