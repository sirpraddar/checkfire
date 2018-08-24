import collections


class bcolors:
    MAGENTA = HEADER = '\033[95m'
    BLUE = OKBLUE = '\033[94m'
    GREEN = OKGREEN = '\033[92m'
    YELLOW = WARNING = '\033[93m'
    RED = FAIL = '\033[91m'
    RESET = ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    CYAN = '\033[96m'
    SLOW_BLINK = '\033[5m'
    RAPID_BLINK = '\033[96m'
    FRAMED = '\033[51m'
    ENCIRCLED = '\033[52m'

    def colorString (text, *args):
        res = ""
        for c in args:
            res = res + c
        return res + text + bcolors.RESET