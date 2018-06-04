from flask import Flask,request,jsonify
import json
from CheckFireCore.TestPackage import TestPackage
import configparser


conf = configparser.ConfigParser()
conf.read('node.conf')

tokens = {}
CFNApp = Flask(__name__)

NULL_LEVEL = 0
INFO_LEVEL = 1
CONTROL_LEVEL = 2
ADMIN_LEVEL = 15


def authLevel():
    token = request.form['token']

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
        return [403, 'Unsufficient privilege level.']

    name = package
    jsonData = request.form['data']
    tp = TestPackage(name,json.loads(jsonData))
    tp.saveToFile()
    return [200, "File Received."]


@CFNApp.route('/execute/<package>', methods=['POST'])
def executelocal(package):
    if authLevel() < CONTROL_LEVEL:
        return [403, 'Unsufficient privilege level.']
    pack = TestPackage('tests/'+package)
    results = pack.executeLocalTests()
    return jsonify(results)


@CFNApp.route('/execute', methods=['POST'])
def execute():
    if authLevel() < CONTROL_LEVEL:
        return [403, 'Unsufficient privilege level.']

    jsonData = request.form['data']
    tp = TestPackage(dict=json.loads(jsonData))
    results = tp.executeLocalTests()
    return jsonify(results)