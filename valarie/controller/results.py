#!/usr/bin/python

import cherrypy
import json
import traceback

from valarie.controller.auth import require
from valarie.controller.messaging import add_message
from valarie.model.results import get_controller_results, \
                                  get_procedure_result

class Results(object):
    @cherrypy.expose
    @require()
    def ajax_get_controller(self, objuuid):
        try:
            return json.dumps(get_controller_results(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_procedure(self, prcuuid, hstuuid):
        try:
            return json.dumps(get_procedure_result(prcuuid, hstuuid))
        except:
            add_message(traceback.format_exc())