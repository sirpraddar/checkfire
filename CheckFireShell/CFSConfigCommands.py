from .CFSCommands import command


class rparam (command):
    def getContextSpace(self):
        return self.CONTEXT_CONFIG

    def execute(self, args, environ, context):
        if len(args) != 3:
            self.println("Usage: cparam add|delete <name>")
            return 1

        if "config" not in context or not context["package"].loaded:
            self.println("You have to load a package and select a configuration first")
            return 2

        action = args[1].lower()
        name = args[2]

        if action == "add":
            context["config"].rparams.append(name)
        elif action == "delete" and name in context["config"].rparams:
            context["config"].rparams.remove(name)
        self.println("command completed.")
        return 0


class cparam (command):
    def getContextSpace(self):
        return self.CONTEXT_CONFIG

    def execute(self, args, environ, context):
        if len(args) < 2 or len(args) > 4 :
            self.println("Usage: cparam add|delete|edit|clear <name> <value>")
            return 1

        if "config" not in context or not context["package"].loaded:
            self.println("You have to load a package and select a configuration first")
            return 2

        action = args[1].lower()
        name = args[2]
        if len(args) == 4:
            value = args[3]
        else:
            value = ""

        if action == "add":
            if value == "":
                self.println("You need to specify a value")
                return 2
            context["config"].cparams[name] = value
        elif action == "edit":
            if value == "":
                self.println("You need to specify a value")
                return 2
            if name not in context["config"].cparams:
                self.println ("parameter not present in configuration")
                return 2
            context["config"].cparams[name] = value
        elif action == "delete":
            context["config"].cparams.pop(name)
        elif action == "clear":
            context["config"].cparams[name] = ""
        self.println ("command completed.")
        return 0
