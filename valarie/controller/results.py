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
        add_message("results controller: get controller results: {0}".format(objuuid))
        try:
            return json.dumps(get_controller_results(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_procedure(self, prcuuid, hstuuid):
        add_message("results controller: get procedure result: prcuuid: {0}, hstuuid: {1}".format(prcuuid, hstuuid))
        try:
            return json.dumps(get_procedure_result(prcuuid, hstuuid))
        except:
            add_message(traceback.format_exc())