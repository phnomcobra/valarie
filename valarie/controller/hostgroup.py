#!/usr/bin/python

import cherrypy
import json
import traceback

from valarie.controller.auth import require
from valarie.controller.messaging import add_message
from valarie.model.hostgroup import get_host_grid

class HostGroup(object):
    @cherrypy.expose
    @require()
    def ajax_get_host_grid(self, objuuid):
        add_message("host group controller: get task host grid: {0}".format(objuuid))
        try:
            return json.dumps(get_host_grid(objuuid))
        except:
            add_message(traceback.format_exc())