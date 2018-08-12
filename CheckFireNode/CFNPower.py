from .CFNApp import CFNApp, checkJson, authLevel, ADMIN_LEVEL
from subprocess import Popen

_POWER_OFF="sleep 1; /usr/bin/poweroff"
_REBOOT="sleep 1; /usr/bin/reboot"

@CFNApp.route('/power/shutdown')
def shutdown():
    checkJson()
    if authLevel() != ADMIN_LEVEL:
        return {'message': 'Insufficient privilege level.', 'error': 403}, 403

    Popen([_POWER_OFF])

    return {'error': 0}, 200


@CFNApp.route('/power/reboot')
def reboot():
    checkJson()
    if authLevel() != ADMIN_LEVEL:
        return {'message': 'Insufficient privilege level.', 'error': 403}, 403

    Popen([_REBOOT])

    return {'error': 0}, 200