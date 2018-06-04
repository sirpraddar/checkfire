from CheckFireShell.bcolors import bcolors
from .Test import Test
from .Config import Config
import base64
from os import chmod,remove,getcwd
from pathlib import Path
import json
from json import JSONDecodeError


def validatePath(path):
    if not Path(path).is_file():
        raise ValueError


def defCallback(test, retCode, stdout):
    pass


class TestPackage:
    def __init__(self,path="",name="", dict={}):
        self.name = name
        self.loaded = False
        self.tests = {}
        self.configs = {}
        self.todo = []
        self.files = {}
        self.remoteToDo = {}
        self.path = "tests/" + self.name

        self.__createdFiles = []
        self.__activeConfigs = []

        try:
            if not path == "" and not dict == {}:
                raise ValueError
            if not path == "":
                self.loadFromFile(path)
                self.loaded = True
                self.path = path
            elif not dict == {}:
                self.tests = dict['tests']
                self.configs = dict['configs']
                self.todo = dict['todo']
                self.files = dict['files']
                self.remoteToDo = dict['remoteToDo']
                self.loaded = True
            elif name == "":
                raise ValueError
        except ValueError:
            return

    def executeLocalTests(self, callback=defCallback):
        wd = getcwd() + "/temp/"
        print("Executing Tests:")
        report = {
            "detailed": {},
            "brief": {"success": 0,
                      "fails": 0,
                      "skipped": 0}
        }

        for c in self.__activeConfigs:
            self.expandFiles(self.configs[c].getRequiredFiles())

        for i in self.todo:
            curTest = self.tests[i]
            for c in curTest.configs:
                for k in self.configs[c].rparams:
                    if k not in curTest.tparams:
                        return (-2, "Missing config parameter {}\n".format(k))

            self.expandFiles(curTest.getRequiredFiles())
            for c in curTest.configs:
                self.expandFiles(self.configs[c].getRequiredFiles())

            for c in self.__activeConfigs:
                if c not in curTest.configs:
                    self.configs[c].deactivate()
                    self.__activeConfigs.remove(c)

            for k in curTest.configs:
                if k not in self.__activeConfigs:
                    self.configs[k].activate()
                    self.__activeConfigs.append(k)

            result = self.tests[i].execTest()
            if result[0] == 0:
                report["brief"]["success"] += 1
            elif result[0] == -1:
                report["brief"]["fails"] += 1
            elif result[0] == -2:
                report["brief"]["skipped"] += 1
            else:
                report["brief"]["fails"] += 1

            callback(self.tests[i], result[0], result[1])
            report["detailed"][i] = (result[0], result[1])
        self.cleanTemp()
        return report

    def cleanTemp(self):
        for i in self.__createdFiles:
            try:
                remove("temp/" + i)
                self.__createdFiles.remove(i)
            except FileNotFoundError:
                pass

    def expandFiles(self, names):
        for i in names:
            self.expandFile(i)

    def expandFile (self, name):
        with open("temp/" + name, "w") as bergof:
            script = base64.b64decode(self.files[name])
            bergof.write(script.decode("ascii"))
            self.__createdFiles.append(name)
        chmod("temp/" + name, 0o700)

    def loadFromFile(self,path):
        validatePath(path)

        file = open (path,'r')
        try:
            testParsed = json.loads(file.read())
        except JSONDecodeError:
            print("Package malformed")
            return
        for k,v in testParsed["tests"].items():
            self.tests[k] = Test(v,k)
        for k,c in testParsed["configs"].items():
            self.configs[k] = Config(k,c)
        self.todo = testParsed["todo"]
        self.files = testParsed["files"]
        self.name = testParsed["name"]
        self.remoteToDo = testParsed["remoteToDo"]
        self.path = path
        self.loaded = True

    def toDict(self):
        dict = {}
        dict["name"] = self.name
        dict["tests"] = {}
        dict["configs"] = {}
        for k,v in self.tests.items():
            dict["tests"][k] = v.toDict()
        for k,v in self.configs.items():
            dict["configs"][k] = v.toDict()
        dict["todo"] = self.todo
        dict["files"] = self.files
        dict["remoteToDo"] = self.remoteToDo

        return dict

    def saveToFile(self, path=""):
        if path == "":
            path= self.path
        file = json.dumps(self.toDict(), indent=3)
        f = open (path, "w")
        f.write(file)

    def appendNewTest(self, name, scriptPath, description):
        self.tests[name] = Test(name=name)
        scriptName = Path(scriptPath).name
        self.tests[name].script = scriptName
        self.tests[name].description = description
        textb64 = base64.b64encode(open(scriptPath, "rb").read())
        self.files[scriptName] = textb64.decode("ascii")

    def renameTest(self,oldname,newname):
        if oldname in self.tests:
            backup = self.tests[oldname]
            self.tests.pop(oldname)
            backup.name = newname
            self.tests[newname] = backup

    def appendNewConfig(self,name, escript, dscript, description):
        conf = Config(name)
        if escript not in self.files:
            self.importFile(escript)
        if dscript not in self.files:
            self.importFile(dscript)

        escript = Path(escript).name
        dscript = Path(dscript).name

        conf.dscript = dscript
        conf.escript = escript
        conf.description = description

        self.configs[name] = conf

    def copyTestFromPackage (self, sourcePack, name):
        test = sourcePack.tests[name]
        for i in test.require:
            self.files[i] = sourcePack.files[i]
        for i in test.configs:
            self.copyConfigFromPackage(sourcePack,i)
            for j in self.configs[i].require:
                self.files[j] = sourcePack.files[j]
        self.files[test.script] = sourcePack.files[test.script]
        self.tests[name] = test

    def copyConfigFromPackage(self,sourcePack,name):
        config = sourcePack.configs[name]
        for i in config.require:
            self.files[i] = sourcePack.files[i]
        self.files[sourcePack.configs[name].escript] = sourcePack.files[sourcePack.configs[name].escript]
        self.files[sourcePack.configs[name].dscript] = sourcePack.files[sourcePack.configs[name].dscript]
        self.configs[name] = sourcePack.configs[name]

    def addTParam (self,pName, pValue):
        self.tests.tparams[pName] = pValue

    def delTParam (self,pName):
        self.tests.pop(pName)

    def __str__(self):
        text = ""
        text += bcolors.colorString("Showing info for package " + self.name + "\n",bcolors.BOLD)

        testSeq = bcolors.colorString("Local Test sequence: ", bcolors.BOLD)
        for i in self.todo:
            testSeq += "{} ".format(i)

        text += bcolors.colorString(testSeq, bcolors.YELLOW)

        text += bcolors.colorString("\nRemote tests sequences:\n",bcolors.BOLD)

        c = 0
        for k,l in self.remoteToDo.items():
            testSeq = "REMOTE {} :: ".format(k)
            for m in l:
                testSeq += "{} ".format(m)
            text += bcolors.colorString(testSeq,bcolors.CYAN if c % 2 else bcolors.YELLOW) + "\n"
            c += 1

        text += bcolors.colorString("\nTest List:\n",bcolors.BOLD)
        for j,i in self.tests.items():
            text += "   {}: {}\n".format(j,i.description)

        text += bcolors.colorString("\nConfig List:\n",bcolors.BOLD)
        for j,i in self.configs.items():
            text += "   {}: {}\n".format(j, i.description)

        text += bcolors.colorString("\nIncluded files:\n",bcolors.BOLD)
        for j,i in self.files.items():
            text += "   {}\n".format(j)
        text += '\n'

        return text

    def importFile(self, path):
        name = Path(path).name
        textb64 = base64.b64encode(open(path,"rb").read())
        self.files[name] = textb64.decode("ascii")