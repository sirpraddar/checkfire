from prompt_toolkit.shortcuts import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter
from prompt_toolkit.styles import style_from_dict
from pygments.token import Token
from CheckFireShell.CFSCommands import *
from CheckFireShell.CFSTestCommands import *
from CheckFireShell.CFSPackageCommands import *
from CheckFireShell.CFSConfigCommands import *
from CheckFireShell.CFSNodes import *
from CheckFireShell.CFSHelp import help
from CheckFireCore.TestPackage import TestPackage
import re
import configparser

CONF_PATH = 'master.conf'

class CFShell:
    def __init__(self):

        self.switch = {
            'help': help,
            #'list': list,
            'load': load,
            'newpackage': newpackage,
            'clonepackage': clonepackage,
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
            'deletefile': deletefile,
            'deletetest': deletetest,
            'deleteconfig': deleteconfig,
            'tedit':tedit,
            'newconfig':newconfig,
            'rparam':rparam,
            'cparam':cparam,
            'tconfig':tconfig,
            'nodelist':nodelist,
            'tfiles': tfiles,
            'nodespower': nodespower,
            'updatenodes': updatenodes,
        }
        self.environ = {
            "config": configparser.ConfigParser(),
        }
        self.context = {
            "package": TestPackage()
        }

        self.environ['config'].read(CONF_PATH)

        self.sorted = contextSorter(self.switch)

        #Colors of prompt terminal
        self.style = style_from_dict({
            Token: '#ff0066',
            #dotmarks token
            Token.Colon: '#fefefe',
            #Test token
            Token.At: '#00ff00',
            #Config token
            Token.Pound: '#ff00ff',
            #Package token
            Token.Username: '#ff0000',
        })

    def get_prompt_tokens(self, cli):
        tokens = []
        tokens.append((Token.Colon, '<'))
        if "package" in self.context and self.context["package"].loaded:
            tokens.append((Token.Username,self.context["package"].name))
            if "test" in self.context:
                tokens.append((Token.Colon,'-'))
                tokens.append((Token.At,self.context["test"].name))
            elif "config" in self.context:
                tokens.append((Token.Colon,'.'))
                tokens.append((Token.Pound, self.context["config"].name))
        tokens.append((Token.Colon,'> : '))
        return tokens

    #main loop of CLI
    def cmdloop(self, stdin=""):
        history = InMemoryHistory()
        returnValues = (0, "")
        while returnValues[0] >= 0:
            # if self.context["package"].loaded == False:
            #     #promptString="<>: "
            #     promptString = []
            # elif self.context.get("test"):
            #     promptString = "<" + self.context["package"].name + "-" + self.context["test"].name + ">"
            #     promptString = bcolors.colorString(promptString,bcolors.YELLOW)
            # elif self.context.get("config"):
            #     promptString = "<" + self.context["package"].name + "%" + self.context["config"].name + ">"
            #     promptString = bcolors.colorString(promptString,bcolors.CYAN)
            # else:
            #     promptString = "<" + self.context["package"].name + ">"
            try:
                text = prompt(get_prompt_tokens=self.get_prompt_tokens,history=history, completer=self.getCompleter(), complete_while_typing=True,style=self.style)
            except (KeyboardInterrupt):
                continue
            except EOFError:
                break

            if text.count("'") % 2 == 1:
                print("Missing quotes.")
                continue

            if text == "":
                continue
            doubleQuoted = text.split("'")
            cc = 0
            arguments = []

            for i in doubleQuoted:
                if cc % 2 == 1:
                    arguments.append(i)
                else:
                    ii = re.sub(r'[ ]+'," ", i)
                    ii = ii.strip()
                    arguments.extend(ii.split(" "))
                cc += 1
            while '' in arguments:
                arguments.remove('')

            if arguments[0] not in self.switch:
                print ("ERROR: Command not recognized or not supported yet.")
                continue
            #execute command if valid
            self.executeCommand(arguments)

        print("Bye.")

    def executeCommand(self, arguments):
        command = self.switch[arguments[0]]()
        try:
            returnValues = command.launch(arguments, self.environ, self.context)
        except KeyboardInterrupt:
            returnValues = command.keyboardInterrupted()
        finally:
            if returnValues[0] == 0:
                print("{}".format(returnValues[1]), end="")
            elif returnValues[0] == 1:
                print("{}) {}".format(returnValues[0], returnValues[1]), end="")
            elif returnValues[0] == 2:
                print("{})ERROR: {}".format(returnValues[0], returnValues[1]), end="")
            return returnValues

    def getCompleter(self):
        if "test" in self.context:
            return WordCompleter(self.sorted.testSpace, ignore_case=True, )
        elif "config" in self.context:
            return WordCompleter(self.sorted.configSpace, ignore_case=True, )
        elif self.context["package"].loaded:
            return WordCompleter(self.sorted.packageSpace, ignore_case=True, )
        else:
            return WordCompleter(self.sorted.globalSpace, ignore_case=True, )



class contextSorter():
    def __init__(self, commands):
        self.globalSpace = []
        self.packageSpace = []
        self.testSpace = []
        self.configSpace = []

        for k,v in commands.items():
            from CheckFireShell.CFSCommands import command
            if v().getContextSpace() & command.CONTEXT_GLOBAL:
                self.globalSpace.append(k)
            if v().getContextSpace() & command.CONTEXT_PACKAGE:
                self.packageSpace.append(k)
            if v().getContextSpace() & command.CONTEXT_TEST:
                self.testSpace.append(k)
            if v().getContextSpace() & command.CONTEXT_CONFIG:
                self.configSpace.append(k)
