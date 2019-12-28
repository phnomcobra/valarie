#!/usr/bin/python

import cherrypy
import json
import traceback

from valarie.controller.auth import require
from valarie.controller.messaging import add_message
from valarie.dao.document import Collection
from valarie.executor.terminal import create_session, \
                                      destroy_session, \
                                      write_file, \
                                      send, \
                                      recv

class Terminal(object):
    @cherrypy.expose
    @require()
    def ajax_create_session(self, hstuuid):
        add_message("terminal controller: create terminal")
        try:
            return json.dumps({"ttyuuid" : create_session(hstuuid, Collection("inventory").find(sessionid = cherrypy.session.id)[0].object)})
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_destroy_session(self, ttyuuid):
        add_message("terminal controller: destroy terminal: {0}".format(ttyuuid))
        try:
            destroy_session(ttyuuid)
            return json.dumps({})
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_send(self, ttyuuid, buffer):
        try:
            send(ttyuuid, buffer)
            return json.dumps({})
        except Exception:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_recv(self, ttyuuid):
        try:
            return recv(ttyuuid)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def put_file(self, file, ttyuuid):
        add_message("terminal controller: upload file: {0}".format(file.filename))
        
        try:
            write_file(ttyuuid, file)
        except:
            add_message(traceback.format_exc())
        
        return json.dumps({})
