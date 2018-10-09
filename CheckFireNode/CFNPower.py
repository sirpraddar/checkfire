#from subprocess import Popen
from os import system
from .CFNApp import checkJson, authLevel, ADMIN_LEVEL
from flask import Blueprint
import json

_POWER_OFF="/usr/bin/env sleep 1; /usr/bin/env poweroff"
_REBOOT="/usr/bin/env sleep 1; /usr/bin/env reboot"

mod_power = Blueprint('power',__name__)

@mod_power.route('/power/shutdown', methods=["POST"])
def shutdown():
    checkJson()
    if authLevel() != ADMIN_LEVEL:
        return {'message': 'Insufficient privilege level.', 'error': 403}, 403

    system(_POWER_OFF)

    return json.dumps({'error': 0}), 200


@mod_power.route('/power/reboot',methods=["POST"])
def reboot():
    checkJson()
    if authLevel() != ADMIN_LEVEL:
        return {'message': 'Insufficient privilege level.', 'error': 403}, 403

    system(_REBOOT)

    return json.dumps({'error': 0}), 200