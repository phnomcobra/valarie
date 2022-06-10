#!/usr/bin/python3

import cherrypy
import json
import traceback

from valarie.router.messaging import add_message
from valarie.controller.procedure import get_task_grid, get_host_grid
from valarie.executor.procedure import get_jobs_grid, queue_procedure

class Procedure(object):
    @cherrypy.expose
    def get_task_grid(self, objuuid):
        try:
            return json.dumps(get_task_grid(objuuid))
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def get_host_grid(self, objuuid):
        try:
            return json.dumps(get_host_grid(objuuid))
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def queue_procedure(self, prcuuid, hstuuid):
        try:
            queue_procedure(hstuuid, prcuuid)
            return json.dumps({})
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def queue_procedures(self, queuelist):
        try:
            for item in json.loads(queuelist):
                try:
                    if "ctruuid" in item:
                        ctruuid = item["ctruuid"]
                    else:
                        ctruuid = None

                    queue_procedure(item["hstuuid"], item["prcuuid"], ctruuid)
                except:
                    add_message(traceback.format_exc())

            return queuelist
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def get_queue_grid(self):
        try:
            return json.dumps(get_jobs_grid())
        except:
            add_message(traceback.format_exc())