from flask import request,abort
import configparser
from CheckFireCore.GlobalSettings import *

NULL_LEVEL = 0
INFO_LEVEL = 1
CONTROL_LEVEL = 2
ADMIN_LEVEL = 15

conf = configparser.ConfigParser()
conf.read(NODE_CONF_PATH)

def authLevel():
    try:
        token = request.json['token']
    except KeyError:
        return NULL_LEVEL
    if token == conf['Security']['AdminToken']:
        return ADMIN_LEVEL
    elif token == conf['Security']['ControlToken']:
        return CONTROL_LEVEL
    elif token == conf['Security']['InfoToken']:
        return INFO_LEVEL
    else:
        return NULL_LEVEL


def checkJson():
    try:
        request.json
    except TypeError:
        abort(400,"Malformed request, please use application/json format.")
