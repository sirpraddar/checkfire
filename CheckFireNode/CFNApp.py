from flask import Flask,request,jsonify
import json
from CheckFireCore.TestPackage import TestPackage
import configparser

CONF_FILE = 'node.conf'

conf = configparser.ConfigParser()
conf.read(CONF_FILE)

tokens = {}
CFNApp = Flask(__name__)

NULL_LEVEL = 0
INFO_LEVEL = 1
CONTROL_LEVEL = 2
ADMIN_LEVEL = 15


def authLevel():
    try:
        token = request.form['token']
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


@CFNApp.route('/load/<package>', methods=['POST'])
def load(package):
    if authLevel() != ADMIN_LEVEL:
        return 'Unsufficient privilege level.', 403

    name = package
    jsonData = request.form['data']
    tp = TestPackage(name,json.loads(jsonData))
    tp.saveToFile()
    return "File Received.", 200


@CFNApp.route('/execute/<package>', methods=['POST'])
def executelocal(package):
    if authLevel() < CONTROL_LEVEL:
        return 'Unsufficient privilege level.', 403
    pack = TestPackage('tests/'+package)
    results = pack.executeLocalTests()
    return jsonify(results)


@CFNApp.route('/execute', methods=['POST'])
def execute():
    if authLevel() < CONTROL_LEVEL:
        return 'Unsufficient privilege level.', 403

    jsonData = request.form['data']
    dict = json.loads(jsonData)
    #print (dict)
    tp = TestPackage(name='temp',dict=dict)
    #print(str(tp))
    results = tp.executeLocalTests()
    return jsonify(results)