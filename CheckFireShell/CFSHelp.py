from .CFSCommands import command
import collections

helpStrings = {
    'newpackage': "Create a new Test Package. Note that it must be saved to be conserved. Usage: createpackage <PackageName>",
    'use': "Select an existing (and imported) Test Package for edit and execution. Usage: use <PackageName>",
    'help': 'Used to list all available command or a command specific help (if any was provided). Usage: help [<command>]',
    #'list': "Prints all available commands Usage: list.",
    'load': "Loads a package file into memory from specified path. Usage: load <PackageFilePath>",
    'info': "Prints details of selected package or test. Usage: info [<TestName>]",
    'exit': "Prints a goodbye message and exits, same as quit.",
    'quit': "Prints a goodbye message and exits, same as exit.",
    'select': "Selects a test for editing. Usage: select <TestName>",
    'deselect': "Unselect the current test.",
    'tparam' : "Add, change, clear or delete a test parameter. Usage: tparam { add|edit <name> <value>, clear|delete <name> }",
    'newtest' : "Create a new test in package using a present script or import test from another package. Usage: newtest script|package <name> <script>",
    'clonetest': "Create a new test copying settings from another test. Usage: clonetest <BaseTestName> <CloneTestName>",
    'save': "Saves the current package configuration to disk. Usage: save [<path>]",
    'testlist': "Add, Remove or rearrange tests order. Usage: testlist add|remove|move [<TestName>] [<Position>]",
    'importfile': "Import an external file to the loaded package. Usage: importfile <FilePath>"
}


#Prints all available commands with help in alphabetical order.
class help(command):
    def getContextSpace(self):
        return self.CONTEXT_GLOBAL | self.CONTEXT_PACKAGE | self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) == 2:
            if args[1] not in helpStrings:
                self.println ("help not available or command does not exists.")
                return 1
            self.println(helpStrings[args[1]])
            return 0
        elif len(args) == 1:
            self.println("Available commands: ")
            sort = collections.OrderedDict(sorted(helpStrings.items()))
            for k,v in sort.items():
                self.println("  " + k + ": " + v)
            return 0
        else:
            self.println("Usage: help [<command>]")
            return 1
