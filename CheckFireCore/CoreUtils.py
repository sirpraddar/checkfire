from pathlib import Path
import subprocess


def validatePath(path):
    if not Path(path).is_file():
        raise ValueError


def execShellCommand(cmd):
    proc = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE)
    return proc.stdout.read(), proc.returncode