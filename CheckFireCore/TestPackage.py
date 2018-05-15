from .bcolors import bcolors
from .Test import Test
from .Config import Config
import base64
from os import chmod,remove,getcwd
from pathlib import Path
import json
from json import JSONDecodeError
import subprocess


def validatePath(path):
    if not Path(path).is_file():
        raise ValueError


class TestPackage:
    def __init__(self,path="",name=""):

        self.name = name
        self.loaded = False
        self.tests = {}
        self.configs = {}
        self.todo = []
        self.files = {}
        self.path = "tests/" + self.name

        self.createdFiles = []
        self.activeConfigs = []

        try:
            if not path == "":
                self.loadFromFile(path)
                self.loaded = True
                self.path = path
            elif name == "":
                raise ValueError
        except ValueError:
            return

    def executeTests(self):
        wd = getcwd() + "/temp/"
        print("Executing Tests:")
        successes = 0
        fails = 0
        skipped = 0
        for i in self.todo:
            curTest = self.tests[i]
            print("{}{:<40}{}".format(bcolors.HEADER,i,bcolors.ENDC), end="")
            #sys.stdout.flush()
            #prepare environment for execution

            self.expandFiles(curTest.getRequiredFiles())

            for c in self.activeConfigs:
                if c not in curTest.configs:
                    self.configs[c].deactivate()

            for k in curTest.configs:
                if k not in self.activeConfigs:
                    self.configs[k].activate()

            result = self.tests[i].execTest()
            if result[0] == 0:
                print("{}[V]{}".format(bcolors.OKGREEN,bcolors.ENDC))
                successes += 1
            elif result[0] == -1:
                print ("{}[X]{}\n{}".format(bcolors.FAIL,bcolors.ENDC,result[1]))
                fails += 1
            elif result[0] == -2:
                print ("{}[S]{}\n{}".format(bcolors.WARNING,bcolors.ENDC,result[1]))
                skipped += 1
            else:
                print ("{}[X]{}\nExit code:{}\n{}".format(bcolors.FAIL,bcolors.ENDC,result[0],result[1]))
                fails += 1

        self.cleanTemp()
        return (successes,fails,skipped)


    def cleanTemp(self):
        for i in self.createdFiles:
            try:
                remove("temp/" + i)
            except FileNotFoundError:
                pass


    def expandFiles(self, names):
        for i in names:
            self.expandFile(i)

    def expandFile (self, name):
        with open("temp/" + name, "w") as bergof:
            script = base64.b64decode(self.files[name])
            bergof.write(script.decode("ascii"))
            self.createdFiles.append(name)
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
        #self.tests = testParsed["tests"]
        for k,c in testParsed["configs"].items():
            self.configs[k] = Config(k,v)
        self.todo = testParsed["todo"]
        self.files = testParsed["files"]
        self.name = testParsed["name"]
        self.path = path
        self.loaded = True

    def toDict(self):
        dict = {}
        dict["name"] = self.name
        dict["tests"] = {}
        for k,v in self.tests.items():
            dict["tests"][k]=v.toDict()
        dict["configs"] = self.configs
        dict["todo"] = self.todo
        dict["files"] = self.files

        return dict

    def saveToFile(self,path=""):

        if path == "":
            path= self.path
        try:
            file = json.dumps(self.toDict(), indent=3)
            f = open (path, "w")
            f.write(file)
        except:
            raise ValueError

    def appendNewTest(self, name, scriptPath, description):
        self.tests[name] = Test()
        scriptName = Path(scriptPath).name
        self.tests[name].script = scriptName
        self.tests[name].description = description
        textb64 = base64.b64encode(open(scriptPath, "rb").read())
        self.files[name] = textb64.decode("ascii")

    def appendNewConfig(self,name, escript, dscript, description):
        pass

    def copyTestFromPackage (self, sourcePack, name):
        test = sourcePack.tests[name]
        for i in test.require:
            self.files[i] = sourcePack.files[i]
        for i in test.configs:
            self.configs[i] = sourcePack.configs[i]
            self.files[sourcePack.configs[i]["EScript"]] = sourcePack.files[sourcePack.configs[i]["EScript"]]
            self.files[sourcePack.configs[i]["DScript"]] = sourcePack.files[sourcePack.configs[i]["DScript"]]
            for j in i.require:
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
        text += "Showing info for package " + self.name + "\n"
        text += "Test List:\n"
        for j,i in self.tests.items():
            text += "   {}: {}\n".format(j,i.description)
        text += '\n'

        text += "Test sequence: "
        for i in self.todo:
            text += "{} ".format(i)
        text += "\n"
        text += "Config List:"
        for j,i in self.configs.items():
            text += "   {}\n".format(j)
        text += '\n'

        text += "Included files:\n"
        for j,i in self.files.items():
            text += "   {}\n".format(j)
        text += '\n'

        return text

    def importFile(self, path):
        name = Path(path).name
        textb64 = base64.b64encode(open(path,"rb").read())
        self.files[name] = textb64.decode("ascii")
