#!/usr/bin/python3

import cherrypy
import traceback
import json

from os import system
from threading import Timer
from valarie.router.messaging import add_message
from valarie.controller.config import get_config

def restart():
    command = get_config()["restartcmd"]
    add_message("Restarting...")
    add_message(command)
    status = system(command)
    add_message(f'status: {status}')

class General(object):
    @cherrypy.expose
    def restart(self):
        add_message("general controller: restarting in 3 seconds...")
        try:
            Timer(3, restart).start()
            return json.dumps({})
        except:
            add_message(traceback.format_exc())
