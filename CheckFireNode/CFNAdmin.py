from .CFNApp import checkJson, authLevel, ADMIN_LEVEL
from subprocess import run, Popen
from .CFNPower import reboot
from flask import Blueprint
import platform

if platform.system() == "Linux":
    _UPDATECMD = ['git', 'pull']
else:
    _UPDATECMD = ['C:\\Program Files\\Git\\cmd\\git.exe', 'pull']
mod_admin = Blueprint('admin',__name__)


@mod_admin.route('/admin/update',methods=["POST"])
def update():
    checkJson()
    if authLevel() != ADMIN_LEVEL:
        return {'message': 'Insufficient privilege level.', 'error': 403}, 403

    run(_UPDATECMD)
    reboot()
    return {'error': 0}, 200