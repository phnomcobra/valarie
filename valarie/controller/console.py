#!/usr/bin/python

import cherrypy
import json
import traceback

from valarie.controller.auth import require
from valarie.controller.messaging import add_message
from valarie.model.console import get_consoles

class Console(object):
    @cherrypy.expose
    @require()
    def ajax_get_consoles(self):
        try:
            return json.dumps(get_consoles())
        except:
            add_message(traceback.format_exc())