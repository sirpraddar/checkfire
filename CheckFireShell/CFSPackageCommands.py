from .CFSCommands import command
from .CFSUtils import checkPathExists
from CheckFireCore.Test import Test
from CheckFireCore.TestPackage import TestPackage
from .CFSCommands import importfile
from .bcolors import bcolors

#Executes the test suite
class go(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if not context["package"].loaded:
            self.println("You have to load a package first")
            return 2

        summary = context["package"].executeLocalTests(self.callback)
        self.println("Tests completed. Summary:")
        self.println(" {} test passed".format(summary["success"]))
        self.println(" {} test failed".format(summary["fails"]))
        self.println(" {} test skipped".format(summary["skipped"]))
        return 0

    def callback (self, test, exitCode, stdout):
        print("{}{:<40}{}".format(bcolors.HEADER, test.name, bcolors.ENDC), end="")

        if exitCode == 0:
            print("{}[V]{}".format(bcolors.OKGREEN,bcolors.ENDC))
        elif exitCode == -1:
            print("{}[X]{}\n{}".format(bcolors.FAIL, bcolors.ENDC, stdout))
        elif exitCode == -2:
            print("{}[S]{}\n{}".format(bcolors.WARNING, bcolors.ENDC, stdout))
        else:
            print("{}[X]{}\nExit code:{}\n{}".format(bcolors.FAIL, bcolors.ENDC, exitCode, stdout))


class newconfig(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if len(args) != 5 and len(args) != 4:
            self.println("Usage: newconfig <name> script <enableScript> <disableScript>")
            self.println("          newconfig <ConfigName> package <PackageName>")
            return 1

        command = args[2]
        name = args[1]
        enableScript = args[3]
        if len(args) == 5:
            disableScript = args[4]

        importEScript = importDScript = False
        if command == "script":
            if enableScript not in context["package"].files:
                if not checkPathExists(enableScript):
                    self.println("Enable script not found.")
                    return 2
                importEScript = True

            if enableScript not in context["package"].files:
                if not checkPathExists(disableScript):
                    self.println("Disable script not found.")
                    return 2
                importDScript = True

            description = input("Please enter this configuration description: ")
            if importEScript:
                importfile().execute(["importfile",enableScript],environ,context)
            if importDScript:
                importfile().execute(["importfile", disableScript], environ, context)

            context["package"].appendNewConfig(name,enableScript,disableScript,description)
            self.println("Config created.")
            return 0

        elif command == "package":
            source = TestPackage("tests/"+enableScript,enableScript)
            if enableScript in context["package"].configs:
                if not input("Configuration already present, do you want to overwrite? (y/n)").upper() == "Y":
                    self.println("Aborted")
                    return 1

            if enableScript not in source.configs:
                self.println("Required configuration not in source package.")
                return 2

            context["package"].copyConfigFromPackage(source, name)

            self.println("Import complete")
            return 0

        else:
            self.println("Please use script or package only.")
            return 2


#Commands regarding TestPackages
class newtest (command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if len(args) != 4:
            self.println("Usage: newtest <name> script <scriptname>")
            self.println("          newtest <TestName> package <PackageName>")
            return 1

        command = args[2]
        name = args[1]
        script = args[3]

        if command == "script":
            if script not in context["package"].files:
                if not checkPathExists(script):
                    self.println("Script not found in package or invalid path.")
                    return 2
                description = input("Please enter this test description: ")
                #importfile().execute(["importfile",script],environ,context)
                context["package"].appendNewTest(name,script,description)

            self.println("Script created.")
            return 0

        elif command == "package":
            source = TestPackage("tests/"+script,script)
            if name in context["package"].tests:
                if not input("Test already present, do you want to overwrite? (y/n)").upper() == "Y":
                    self.println("Aborted")
                    return 1

            if name not in source.tests:
                self.println("Required test not in source package.")
                return 2

            context["package"].copyTestFromPackage(source,name)

            self.println("Import complete")
            return 0

        else:
            self.println("Please use script or package only.")
            return 2


class deletetest(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: deletetest <TestName>")
            return 2

        name = args[1]

        if name not in context["package"].tests:
            self.println("Test not found in package.")
            return 1

        context["package"].tests.pop(name)
        self.println("Test deleted.")
        return 0


class deleteconfig(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: deleteconfig <ConfigurationName>")
            return 2

        name = args[1]

        if name not in context["package"].configs:
            self.println("Configuration not found in package.")
            return 1

        context["package"].configs.pop(name)
        self.println("Configuration deleted.")
        return 0


class deletefile(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: deletefile <FileName>")
            return 2

        name = args[1]

        if name not in context["package"].files:
            self.println("File not found in package.")
            return 1

        for k,i in context["package"].tests.items():
            if i.script == name:
                self.println("Can't delete, file {} is the {} test script.".format(name,k))
                return 1
            for j in i.require:
                if j == name:
                    self.println("Can't delete, file {} is required by {}".format(name,k))

        for k, i in context["package"].configs.items():
            if i.escript == name or i.dscript == name:
                self.println("Can't delete, file {} is the {} config script.".format(name, k))
                return 1
            for j in i.require:
                if j == name:
                    self.println("Can't delete, file {} is required by {}".format(name, k))
                    return 1

        context["package"].files.pop(name)
        self.println("File deleted.")
        return 0


class clonetest(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if len(args) != 3:
            self.println("Usage: clonetest <BaseTest> <CloneTest>")
            return 1

        old = args[1]
        new = args[2]

        if old not in context["package"].tests:
            self.println("Base Test not in selected package.")
            return 2

        context["package"].tests[new] = Test(context["package"].tests[old].toDict(), new)
        self.println("Clone complete.")
        return 0


class testlist (command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE | self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) > 4 or len(args) <= 2 :
            self.println("Usage: testlist add|remove|move [<TestName>] [<Position>]")
            return 1

        command = args[1]
        name = ""
        pos = -1

        todo = context["package"].todo

        if type(args[2]) is int:
            pos = int (args[2])
        elif type(args[2]) is str:
            name = args[2]
            if len(args) == 4:
                pos = int(args[3])

        if command == "add":
            if name not in context["package"].tests:
                self.println("Test not in package.")
                return 2

            if pos >= 0 and pos < len(todo):
                todo.insert(pos,name)
            else:
                todo.append(name)
        elif command == "remove":
            if name not in context["package"].todo:
                self.println("Test not in ToDo list")
                return 2
            todo.remove(name)
        elif command == "move":
            if name not in todo or pos < 0 or pos > len(todo):
                self.println("Test not in todo list or position not valid.")
                return 2
            todo.remove(name)
            todo.insert(pos,name)

        return 0


class nodelist (command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if len(args) > 5 or len(args) <= 2 :
            self.println("Usage: nodelist <Node> add|move|remove|delete [<TestName>] [<Position>]")
            return 1

        remote = args[1]
        command = args[2]
        name = ""
        pos = -1

        if remote in context["package"].remoteToDo:
            todo = context["package"].remoteToDo[remote]
        elif command == "add":
            todo = []
            context["package"].remoteToDo[remote] = todo

        if len(args) > 3:
            if type(args[3]) is int:
                pos = int (args[3])
            elif type(args[3]) is str:
                name = args[3]
                if len(args) == 5:
                    pos = int(args[4])

        if command == "add":
            if name not in context["package"].tests:
                self.println("Test not in package.")
                return 2

            if pos >= 0 and pos < len(todo):
                todo.insert(pos,name)
            else:
                todo.append(name)
        elif command == "remove":
            if name not in context["package"].todo:
                self.println("Test not in this ToDo list")
                return 2
            todo.remove(name)
            if not todo:
                context["package"].remoteToDo.pop(remote)
        elif command == "move":
            if name not in todo or pos < 0 or pos > len(todo):
                self.println("Test not in todo list or position not valid.")
                return 2
            todo.remove(name)
            todo.insert(pos,name)
        elif command == "delete":
            if remote not in context["package"].remoteToDo:
                self.println("Non existant ToDo list.")
                return 2
            context["package"].remoteToDo.pop(remote)
        return 0


class newpackage(command):
    def getContextSpace(self):
        return self.CONTEXT_GLOBAL

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: createpackage <PackageName>")
            return 1

        print (args[1])
        newpack = TestPackage(name=args[1])
        newpack.saveToFile()
        context["package"] = newpack

        return 0