#!/usr/bin/python3

import cherrypy
import json
import traceback

from valarie.router.messaging import add_message
from valarie.controller.results import get_controller_results, get_procedure_result, get_result

class Results(object):
    @cherrypy.expose
    def get_controller(self, objuuid):
        try:
            return json.dumps(get_controller_results(objuuid))
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def get_procedure(self, prcuuid, hstuuid):
        try:
            return json.dumps(get_procedure_result(prcuuid, hstuuid))
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def get_result(self, resuuid):
        try:
            return json.dumps(get_result(resuuid))
        except:
            add_message(traceback.format_exc())
