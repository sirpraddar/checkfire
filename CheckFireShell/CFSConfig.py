from .CFSCommands import command


class cparam (command):
    def getContextSpace(self):
        return self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) < 2 or len(args) > 4 :
            self.println("Usage: cparam add|delete|edit|clear <name> <value>")
            return 1

        if "config" not in context or not context["package"].loaded:
            self.println("You have to load a package and select a configuration first")
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
            context["config"].tparams[name] = value
        elif action == "edit":
            if value == "":
                self.println("You need to specify a value")
                return 2
            if name not in context["config"].tparams:
                self.println ("parameter not present in test")
                return 2
            context["config"].tparams[name] = value
        elif action == "delete":
            context["config"].tparams.pop(name)
        elif action == "clear":
            context["config"].tparams[name] = ""
        self.println ("command completed.")
        return 0
