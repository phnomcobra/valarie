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
        add_message("task controller: get task host grid: {0}".format(objuuid))
        try:
            return json.dumps(get_host_grid(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_execute_task(self, tskuuid, hstuuid):
        add_message("task controller: execute task: hstuuid: {0}, tskuuid: {1}".format(hstuuid, tskuuid))
        try:
            return json.dumps(execute(tskuuid, hstuuid, Collection("users").find(sessionid = cherrypy.session.id)[0].object))
        except:
            add_message(traceback.format_exc())