#!/usr/bin/python

import cherrypy
import json
import traceback

from valarie.controller.messaging import add_message
from valarie.controller.auth import require
from valarie.model.task import get_host_grid
from valarie.executor.task import execute
from valarie.dao.document import Collection

class Task(object):
    @cherrypy.expose
    @require()
    def ajax_get_host_grid(self, objuuid):
        try:
            return json.dumps(get_host_grid(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_execute_task(self, tskuuid, hstuuid):
        try:
            return json.dumps(execute(tskuuid, hstuuid, Collection("inventory").find(sessionid = cherrypy.session.id)[0].object))
        except:
            add_message(traceback.format_exc())