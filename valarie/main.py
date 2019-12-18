#!/usr/bin/python

import cherrypy
import os
import signal

from valarie.controller.root import Root
from valarie.executor.timers import cancel_timers

def start():
    signal.signal(signal.SIGINT, cancel_timers)
    signal.signal(signal.SIGTERM, cancel_timers)

    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    config = {
        'log.screen': False,
        'tools.staticdir.on' : True,
        'tools.sessions.on' : True,
        'tools.sessions.locking' : 'explicit',
        'tools.auth.on' : True,
        'tools.staticdir.dir' : os.path.join(current_dir, './static'),
        'server.thread_pool' : 100,
        'server.socket_host' : '0.0.0.0',
        'server.socket_port' : 443,
        'server.ssl_module' : 'builtin',
        'server.ssl_certificate' : os.path.join(current_dir, './ssl/cert.pem'),
        'server.ssl_private_key' : os.path.join(current_dir, './ssl/privkey.pem')
    }
    
    cherrypy.config.update(config)
    
    cherrypy.quickstart(Root())
