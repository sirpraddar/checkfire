from flask import Flask,request,jsonify,abort
import json
from CheckFireCore.TestPackage import TestPackage
from .CFNUtils import *
import configparser

from .CFNPower import mod_power
from .CFNAdmin import mod_admin

tokens = {}
CFNApp = Flask(__name__)
CFNApp.register_blueprint(mod_power)
CFNApp.register_blueprint(mod_admin)

@CFNApp.route('/load/<package>', methods=['POST'])
def load(package):
    checkJson()
    if authLevel() != ADMIN_LEVEL:
        return 'Unsufficient privilege level.', 403

    name = package
    jsonData = request.json['data']
    tp = TestPackage(name,jsonData)
    tp.saveToFile()
    return "File Received.", 200


@CFNApp.route('/execute/<package>', methods=['POST'])
def executelocal(package):
    checkJson()
    if authLevel() < CONTROL_LEVEL:
        return 'Unsufficient privilege level.', 403
    pack = TestPackage('tests/'+package)
    results = pack.executeLocalTests()
    return jsonify(results)


@CFNApp.route('/execute', methods=['POST'])
def execute():
    checkJson()
    if authLevel() < CONTROL_LEVEL:
        return 'Unsufficient privilege level.', 403

    dict = request.json['data']
    #dict = json.loads(jsonData)
    #print (dict)
    tp = TestPackage(name='temp',dict=dict)
    #print(str(tp))
    results = tp.executeLocalTests()
    return jsonify(results)