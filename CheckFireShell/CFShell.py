from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
from CheckFireShell.CFSCommands import *
from CheckFireShell.CFSTestCommands import *
from CheckFireShell.CFSPackageCommands import *
from CheckFireShell.CFSHelp import help
from CheckFireCore.TestPackage import TestPackage
import re

class CFShell:
    def __init__(self):

        self.switch = {
            'help': help,
            #'list': list,
            'load': load,
            'newpackage': newpackage,
            'use': use,
            'info': info,
            'select': select,
            'deselect': deselect,
            'exit': exit,
            'quit': exit,
            'tparam': tparam,
            'newtest': newtest,
            'clonetest': clonetest,
            'save': save,
            'testlist' : testlist,
            'importfile': importfile,
            'go': go,
        }
        self.environ = {}
        self.context = {
            "package":TestPackage()
        }

        self.sorted = contextSorter(self.switch)

    #main loop of CLI
    def cmdloop(self):
        history = InMemoryHistory()
        returnValues = (0, "")
        while returnValues[0] >= 0:
            if self.context["package"].loaded == False:
                promptString="<>: "
            elif not self.context.get("test"):
                promptString = "<" + self.context["package"].name + ">: "
            else:
                promptString = "<" + self.context["package"].name + "-" + self.context["test"].name + ">: "
            try:
                text = prompt(promptString,history=history, completer=self.getCompleter(), complete_while_typing=True)
            except (KeyboardInterrupt):
                continue
            except EOFError:
                break
            #Some handling of white-spaces
            text = re.sub(r'[ ]+'," ", text)
            text = text.strip()
            arguments = text.split(" ")
            if text == "":
                continue
            if arguments[0] not in self.switch:
                print ("ERROR: Command not recognized or not supported yet.")
                continue
            #execute command if valid
            returnValues = self.switch[arguments[0]]().launch(arguments, self.environ, self.context)
            if returnValues[0] == 0:
                print ("{}".format(returnValues[1]), end="")
            elif returnValues[0] == 1:
                print("{}) {}".format(returnValues[0], returnValues[1]), end="")
            elif returnValues[0] == 2:
                print("{})ERROR: {}".format(returnValues[0], returnValues[1]), end="")

        print("Bye.")

    def getCompleter(self):
        if "test" in self.context:
            return WordCompleter(self.sorted.testSpace, ignore_case=True, )
        elif self.context["package"].loaded:
            return WordCompleter(self.sorted.packageSpace, ignore_case=True, )
        else:
            return WordCompleter(self.sorted.globalSpace, ignore_case=True, )



class contextSorter():
    def __init__(self, commands):
        self.globalSpace = []
        self.packageSpace = []
        self.testSpace = []

        for k,v in commands.items():
            from CheckFireShell.CFSCommands import command
            if v().getContextSpace() & command.CONTEXT_GLOBAL:
                self.globalSpace.append(k)
            if v().getContextSpace() & command.CONTEXT_PACKAGE:
                self.packageSpace.append(k)
            if v().getContextSpace() & command.CONTEXT_TEST:
                self.testSpace.append(k)
