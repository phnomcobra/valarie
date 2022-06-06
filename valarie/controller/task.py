#!/usr/bin/python3

import cherrypy
import json
import traceback

from valarie.controller.messaging import add_message
from valarie.model.task import get_host_grid
from valarie.executor.task import execute

class Task(object):
    @cherrypy.expose
    def get_host_grid(self, objuuid):
        try:
            return json.dumps(get_host_grid(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    def execute_task(self, tskuuid, hstuuid):
        try:
            return json.dumps(execute(tskuuid, hstuuid))
        except:
            add_message(traceback.format_exc())
