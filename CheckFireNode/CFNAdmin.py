from .CFNApp import CFNApp, checkJson, authLevel, ADMIN_LEVEL
from subprocess import run, Popen
from .CFNPower import _REBOOT

_UPDATECMD = "git pull"

@CFNApp.route('/admin/update')
def update():
    checkJson()
    if authLevel() != ADMIN_LEVEL:
        return {'message': 'Insufficient privilege level.', 'error': 403}, 403

    run([_UPDATECMD])
    Popen([_REBOOT])
    return {'error': 0}, 200