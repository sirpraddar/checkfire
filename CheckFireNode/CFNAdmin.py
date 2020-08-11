from .CFNApp import checkJson, authLevel, ADMIN_LEVEL
from subprocess import run, Popen
from .CFNPower import reboot
from flask import Blueprint

_UPDATECMD = ['git', 'pull']
mod_admin = Blueprint('admin',__name__)


@mod_admin.route('/admin/update',methods=["POST"])
def update():
    checkJson()
    if authLevel() != ADMIN_LEVEL:
        return {'message': 'Insufficient privilege level.', 'error': 403}, 403

    run(_UPDATECMD)
    reboot()
    return {'error': 0}, 200