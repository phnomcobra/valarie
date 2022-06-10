#!/usr/bin/python3

import cherrypy
import json
import traceback

from valarie.router.messaging import add_message
from valarie.controller.console import get_consoles

class Console(object):
    @cherrypy.expose
    def get_consoles(self):
        try:
            return json.dumps(get_consoles())
        except:
            add_message(traceback.format_exc())
