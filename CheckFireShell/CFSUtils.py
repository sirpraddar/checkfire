from pathlib import Path

def checkPathExists(path):
    return Path(path).is_file()