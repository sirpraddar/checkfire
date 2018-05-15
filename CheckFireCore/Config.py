from os import getcwd
import subprocess

class Config:
    def __init__(self, name, dict = {}):
        self.name = name
        self.escript = ""
        self.dscript = ""
        self.require = []
        self.description = ""
        self.rparams = []

        if dict != {}:
            self.escript = dict["escript"]
            self.dscript = dict["dscript"]
            self.require = dict["require"]
            self.description = dict["description"]
            self.rparams = dict["rparams"]

    def toDict(self):
        dict = {}
        dict["name"] = self.name
        dict["escript"] = self.escript
        dict["dscript"] = self.dscript
        dict["require"] = self.require
        dict["description"] = self.description
        dict["rparams"] = self.rparams

        return dict


    def activate(self):
        wd = getcwd() + "/temp/"
        subprocess.run(wd + self.escript, cwd=wd, stdout=subprocess.DEVNULL)

    def deactivate(self):
        wd = getcwd() + "/temp/"
        subprocess.run(wd + self.dscript, cwd=wd, stdout=subprocess.DEVNULL)
