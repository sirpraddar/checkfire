from pathlib import Path

def validatePath(path):
    if not Path(path).is_file():
        raise ValueError