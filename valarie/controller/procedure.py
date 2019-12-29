#!/usr/bin/python

import cherrypy
import json
import traceback

from valarie.controller.auth import require
from valarie.controller.messaging import add_message
from valarie.dao.document import Collection
from valarie.model.procedure import get_task_grid, get_host_grid
from valarie.executor.procedure import get_jobs_grid, queue_procedure

class Procedure(object):
    @cherrypy.expose
    @require()
    def ajax_get_task_grid(self, objuuid):
        add_message("procedure controller: get procedure task grid: {0}".format(objuuid))
        try:
            return json.dumps(get_task_grid(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_host_grid(self, objuuid):
        add_message("procedure controller: get procedure host grid: {0}".format(objuuid))
        try:
            return json.dumps(get_host_grid(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_queue_procedure(self, prcuuid, hstuuid):
        add_message("procedure controller: queuing procedure: hstuuid: {0}, prcuuid: {1}".format(hstuuid, prcuuid))
        try:
            queue_procedure(hstuuid, prcuuid, Collection("inventory").find(sessionid = cherrypy.session.id)[0].object)
            return json.dumps({})
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_queue_procedures(self, queuelist):
        try:
            for item in json.loads(queuelist):
                try:
                    if "ctruuid" in item:
                        ctruuid = item["ctruuid"]
                    else:
                        ctruuid = None
                    
                    add_message("procedure controller: queuing procedure: hstuuid: {0}, prcuuid: {1}".format(item["hstuuid"], item["prcuuid"]))
                    
                    queue_procedure(item["hstuuid"], item["prcuuid"], Collection("inventory").find(sessionid = cherrypy.session.id)[0].object, ctruuid)
                except:
                    add_message(traceback.format_exc())
        
            return queuelist
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_queue_grid(self):
        try:
            return json.dumps(get_jobs_grid())
        except:
            add_message(traceback.format_exc())
