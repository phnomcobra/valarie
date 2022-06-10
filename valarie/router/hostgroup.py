#!/usr/bin/python3

import cherrypy
import json
import traceback

from valarie.router.messaging import add_message
from valarie.controller.hostgroup import get_host_grid

class HostGroup(object):
    @cherrypy.expose
    def get_host_grid(self, objuuid):
        try:
            return json.dumps(get_host_grid(objuuid))
        except:
            add_message(traceback.format_exc())
