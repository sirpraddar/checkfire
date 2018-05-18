from .CFSCommands import command


class tedit (command):
    def getContextSpace(self):
        return self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) != 3:
            self.println("Usage: tedit name|desc <Value>")
            self.println("       tedit negate true|false|0|1")
            return 2

        command = args[1]
        value = args[2]

        if command == "name":
            context["package"].renameTest(context["test"].name,value)
            return 0
        elif command == "desc":
            context["test"].description = value
            return 0
        elif command == "negate":
            if value == "true" or value == 1:
                context["test"].negate = True
                return 0
            elif value == "false" or value == 0:
                context["test"].negate = False
                return 0
            else:
                self.println("Please use true|1 or false|0")
                return 1
        else:
            self.println("Option not recognized. Please use name,description,script,negate")
            return 1


class tparam (command):
    def getContextSpace(self):
        return self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) < 2 or len(args) > 4 :
            self.println("Usage: tparam add|delete|edit|clear <name> <value>")
            return 1

        if "test" not in context or not context["package"].loaded:
            self.println("You have to load a package and select a test first")
            return 2

        action = args[1].lower()
        name = args[2].upper()
        if len(args) == 4:
            value = args[3]
        else:
            value = ""

        if action == "add":
            if value == "":
                self.println("You need to specify a value")
                return 2
            context["test"].tparams[name] = value
        elif action == "edit":
            if value == "":
                self.println("You need to specify a value")
                return 2
            if name not in context["test"].tparams:
                self.println ("parameter not present in test")
                return 2
            context["test"].tparams[name] = value
        elif action == "delete":
            context["test"].tparams.pop(name)
        elif action == "clear":
            context["test"].tparams[name] = ""
        self.println ("command completed.")
        return 0


class tfiles(command):
    def getContextSpace(self):
        return self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) !=3:
            self.println("Usage: tfiles add|delete <FileName>")

        command = args[1]
        file = args[2]

        if not context["package"].loaded or "test" not in context:
            self.println ("You have to select a test first")
            return 2
        if command == "add":
            if file not in context["package"].files:
                self.println("Specified file not in package, you must import it first.")
                return 2
            context["test"].required.append(file)
            self.println("File successfully added.")
            return 0
        elif command == "delete":
            if file in context["test"].required:
                context["test"].remove(file)
                self.println("File successfully removed")
                return 0
        else:
            self.println("Please use add or delete")
            return 2


class tconfig(command):
    def getContextSpace(self):
        return self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) !=3:
            self.println("Usage: tconfig add|delete <ConfigName>")

        command = args[1]
        config = args[2]

        if not context["package"].loaded or "test" not in context:
            self.println ("You have to select a test first")
            return 2
        if command == "add":
            if config not in context["package"].configs:
                self.println("Specified file not in package, you must import it first.")
                return 2
            context["test"].configs.append(config)
            self.println("Config successfully added.")
            return 0
        elif command == "delete":
            if config in context["test"].config:
                context["test"].remove(config)
                self.println("Config successfully unlinked from test.")
                return 0
        else:
            self.println("Please use add or delete")
            return 2
