#!/usr/bin/python

import cherrypy
import os
import signal

from valarie.controller.root import Root
from valarie.executor.timers import cancel_timers
from valarie.controller.messaging import add_message
from valarie.model.config import (
    get_public_key, 
    get_private_key, 
    get_host, 
    get_port, 
    ssl_enabled
)

def shutdown(number, frame):
    add_message("Shutting down...")
    cancel_timers()
    cherrypy.engine.exit()

def start():
    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    current_dir = os.path.dirname(os.path.abspath(__file__))

    config = {
        'log.screen': False,
        'tools.staticdir.on' : True,
        'tools.sessions.on' : True,
        'tools.sessions.locking' : 'explicit',
        'tools.auth.on' : True,
        'tools.staticdir.dir' : os.path.join(current_dir, './static'),
        'server.thread_pool' : 100,
        'server.socket_host' : get_host(),
        'server.socket_port' : get_port()
    }

    if ssl_enabled():
        open(
            os.path.join(current_dir, './ssl/cert.pem'),
            'w'
        ).write(get_public_key())
        
        open(
            os.path.join(current_dir, './ssl/privkey.pem'),
            'w'
        ).write(get_private_key())

        config['server.ssl_module'] = 'builtin'
        config['server.ssl_certificate'] = os.path.join(current_dir, './ssl/cert.pem')
        config['server.ssl_private_key'] = os.path.join(current_dir, './ssl/privkey.pem')
    
    cherrypy.config.update(config)
    
    cherrypy.quickstart(Root())
