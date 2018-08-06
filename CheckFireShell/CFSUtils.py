from pathlib import Path
import re


def checkPathExists(path):
    return Path(path).is_file()


def checkPureName(name):
    pattern = re.compile("^[A-Za-z0-9]+$")
    return pattern.match(name)