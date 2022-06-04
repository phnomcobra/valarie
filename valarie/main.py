#!/usr/bin/python

import cherrypy
import os

from valarie.controller.root import Root
from valarie.executor.timers import cancel_timers
from valarie.model.config import get_host, get_port

def start():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    config = {
        'log.screen': True,
        'tools.staticdir.on' : True,
        'tools.sessions.on' : True,
        'tools.sessions.locking' : 'explicit',
        'tools.staticdir.dir' : os.path.join(current_dir, './static'),
        'server.thread_pool' : 100,
        'server.socket_host' : get_host(),
        'server.socket_port' : get_port()
    }
    
    cherrypy.config.update(config)
    cherrypy.engine.subscribe('stop', cancel_timers)
    cherrypy.quickstart(Root())

