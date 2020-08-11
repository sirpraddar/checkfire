from .CFSCommands import command
from CheckFireCore.Node import shutdownAllNodes,rebootAllNodes,updateAllNodes,pingAllNodes

class nodespower (command):
    def getContextSpace(self):
        return self.CONTEXT_GLOBAL + self.CONTEXT_PACKAGE + self.CONTEXT_CONFIG + self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) != 2:
            self.println("Usage: nodespower shutdown | reboot")
            return 1

        powercommand = args[1]
        if 'shutdown' == powercommand:
            shutdownAllNodes()
        elif 'reboot' == powercommand:
            rebootAllNodes()
        else:
            self.println("Please use shutdown or reboot")
            return 2
        self.println(powercommand + ' issued.')
        return 0


class updatenodes(command):
    def getContextSpace(self):
        return self.CONTEXT_GLOBAL + self.CONTEXT_PACKAGE + self.CONTEXT_CONFIG + self.CONTEXT_TEST

    def execute(self, args, environ, context):
        if len(args) != 1:
            self.println("Usage: updatenodes")
            return 1

        updateAllNodes()
        return 0

class pingnodes(command):
    def getContextSpace(self):
        return self.CONTEXT_GLOBAL + self.CONTEXT_PACKAGE + self.CONTEXT_CONFIG + self.CONTEXT_TEST

    def execute(self, args, environ, context):
        ret = pingAllNodes()
        for k,v in ret.items():
            self.println(k + " : " + v)
        return 0