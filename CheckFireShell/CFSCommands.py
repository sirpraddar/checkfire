import collections
from .CFSUtils import checkPathExists

#Handles Shell stuff
class command ():

    CONTEXT_GLOBAL = 1
    CONTEXT_PACKAGE = 2
    CONTEXT_TEST = 4
    CONTEXT_CONFIG = 8

    def __init__(self):
        self.stdout = ""
        self.contextspace = 0

    def print(self, string):
        self.stdout +=string

    def println (self, string):
        self.print(string)
        self.print("\n")

    def launch (self,args,environ,context):
        code = self.execute(args,environ,context)
        return (code,self.stdout)

    def execute(self, args, environ, context):
        raise NotImplementedError("You are not supposed to use this class directly.")

    def getContextSpace(self):
        raise NotImplementedError("You are not supposed to use this class directly.")

    def keyboardInterrupted(self):
        self.println("Keyboard Interrupted")
        return (1,self.stdout)


#Commands regarding Tests
class select (command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE | self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: select <TestName>|<ConfigName>")
            return 1
        if not context["package"].loaded:
            self.println("No package loaded, please load a test package first.")
            return 2
        package = context["package"]
        test = args[1]
        if test in package.tests:
            test = context["package"].tests[test]
            context["test"] = test
            try:
                context.pop("config")
            except KeyError:
                pass
        elif test in package.configs:
            test = context["package"].configs[test]
            context["config"] = test
            try:
                context.pop("test")
            except KeyError:
                pass
        else:
            self.println("test or configuration not found in package.")
            return 1

        return 0


class deselect(command):
    def getContextSpace(self):
        return self.CONTEXT_TEST + self.CONTEXT_CONFIG

    def execute(self, args, environ, context):
        try:
            context.pop("test")
        except KeyError:
            pass
        try:
            context.pop("config")
        except KeyError:
            pass
        return 0


class use(command):
    def getContextSpace(self):
        return self.CONTEXT_GLOBAL

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: use <PackageName>")
            return 1
        path = "tests/"+args[1]
        if checkPathExists(path):
            from CheckFireCore.TestPackage import  TestPackage
            context["package"] = TestPackage()
            context["package"].loadFromFile(path)
            return 0
        else:
            self.println("Test Package not found.")
            return 1


class info(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE | self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) == 2:
            test = args[1]
        if context["package"].loaded and len(args) == 1:
            self.print(str(context["package"]))
            return 0
        elif context["package"].loaded and test == "." and "test" in context:
            self.print(str(context["test"]))
            return 0
        elif context["package"].loaded and test == "." and "config" in context:
            self.print(str(context["config"]))
            return 0
        elif context["package"].loaded and test in context["package"].tests:
            self.print(str(context["package"].tests[test]))
            return 0
        elif context["package"].loaded and test in context["package"].configs:
            self.print(str(context["package"].configs[test]))
            return 0
        elif context["package"].loaded:
            self.println("The package does not contain specified test, sorry")
            return 1
        else:
            self.println("You have to select a package first")
            return 1


#Commands regarding packageFiles
class load(command):
    def getContextSpace(self):
        return self.CONTEXT_GLOBAL

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: load <TestPackageFile>")
            return 1
        path = args[1]
        if not checkPathExists(path):
            self.println("The provided file does not exist.")
            return 2

        context["package"].loadFromFile(path)
        return 0


class save(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE | self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) > 2:
            self.println("Usage: save [<SavePath>]")
            return 1

        if not context["package"].loaded:
            self.println("You have to use or load a package first")
            return 2
        try:
            if len(args) == 2:
                path = "tests/" + args[1]
                context["package"].saveToFile(path)
            else:
                context["package"].saveToFile()
        except ValueError:
            self.println("There was a problem saving, file has not been overwritten.")
            return 2
        self.println("File saved correctly.")
        return 0


class importfile(command):
    def getContextSpace(self):
        return self.CONTEXT_PACKAGE

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: importfile <Path>")
            return 1
        path = args[1]
        if not checkPathExists(path):
            self.println("File not exists")
            return 2

        context["package"].importFile(path)
        try:
            context["package"].saveToFile()
        except ValueError:
            self.println("File was imported but not saved.")
            return 1
        self.println("File successfully imported.")
        return 0



class exit(command):
    def getContextSpace(self):
        return self.CONTEXT_GLOBAL | self.CONTEXT_PACKAGE | self.CONTEXT_TEST

    def execute(self, args, environ, context):
        return -1
