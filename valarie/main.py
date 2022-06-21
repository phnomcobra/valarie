#!/usr/bin/python3

import cherrypy
import os

from valarie.router.root import Root
from valarie.router.messaging import add_message
from valarie.executor.timers import cancel_timers
from valarie.controller.config import get_host, get_port

def on_cherrypy_log(msg, level):
    add_message(f'<font color="red">{msg}</font>')

def start():
    current_dir = os.path.dirname(os.path.abspath(__file__))

    config = {
        'log.screen': False,
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
    cherrypy.engine.subscribe('log', on_cherrypy_log)
    cherrypy.quickstart(Root())
