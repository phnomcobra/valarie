#!/usr/bin/python

import cherrypy
import json
import traceback

from valarie.controller.messaging import add_message
from valarie.model.controller import (
    get_procedure_grid,
    get_host_grid,
    get_tiles
)

class Controller(object):
    @cherrypy.expose
    def get_procedure_grid(self, objuuid):
        try:
            return json.dumps(get_procedure_grid(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    def get_host_grid(self, objuuid):
        try:
            return json.dumps(get_host_grid(objuuid))
        except:
            add_message(traceback.format_exc())
        
    @cherrypy.expose
    def get_tiles(self, objuuid):
        try:
            return json.dumps(get_tiles(objuuid))
        except:
            add_message(traceback.format_exc())
