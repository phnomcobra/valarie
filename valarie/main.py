#!/usr/bin/python3
"""This module configures and starts the web server."""
import logging
import logging.handlers
import os
from multiprocessing import set_start_method

import cherrypy

from valarie.router.root import Root
from valarie.executor.timers import cancel_timers
from valarie.executor.procedure import start_timer as start_procedures_worker
from valarie.executor.results import start_timer as start_results_worker
from valarie.dao.document import Collection
from valarie.controller.inventory import unlock, create_container
from valarie.controller import logging as app_logger
from valarie.controller.config import (
    get_host,
    get_port,
    create_config,
    create_console_template,
    create_task_template,
    create_settings_container
)

def on_cherrypy_log(msg, level):
    """This function subscribes the logger functions to the log
    channel on cherrypy's bus."""
    if level == 20:
        app_logger.info(msg)
    else:
        app_logger.error(msg)

def init_collections():
    """Initialize the collections and default inventory objects."""
    datastore = Collection("datastore")
    datastore.create_attribute("type", "['type']")

    results = Collection("results")
    results.create_attribute("tskuuid", "['task']['objuuid']")
    results.create_attribute("prcuuid", "['procedure']['objuuid']")
    results.create_attribute("hstuuid", "['host']['objuuid']")

    inventory = Collection("inventory")
    inventory.create_attribute("parent", "['parent']")
    inventory.create_attribute("type", "['type']")
    inventory.create_attribute("name", "['name']")

    if not inventory.find(parent="#"):
        create_container("#", "Root")

    if not inventory.find(type="config"):
        create_config()
        create_console_template()
        create_task_template()
        create_settings_container()

    unlock()

def start():
    """This function configures and starts the web server."""
    current_dir = os.path.dirname(os.path.abspath(__file__))

    set_start_method('spawn')
    init_collections()
    start_procedures_worker()
    start_results_worker()

    config = {
        'log.screen': False,
        'tools.staticdir.on': True,
        'tools.sessions.on': True,
        'tools.sessions.locking': 'explicit',
        'tools.staticdir.dir': os.path.join(current_dir, './static'),
        'server.thread_pool': 100,
        'server.socket_host': get_host(),
        'server.socket_port': get_port()
    }

    access_handler = logging.handlers.TimedRotatingFileHandler(
        'access.log',
        when="S",
        interval=30,
        backupCount=10
    )
    cherrypy.log.access_log.addHandler(access_handler)

    app_handler = logging.handlers.TimedRotatingFileHandler(
        'app.log',
        when="S",
        interval=30,
        backupCount=10
    )
    logger = logging.getLogger('app')
    logger.addHandler(app_handler)
    logger.setLevel(logging.DEBUG)

    cherrypy.config.update(config)
    cherrypy.engine.subscribe('stop', cancel_timers)
    cherrypy.engine.subscribe('log', on_cherrypy_log)
    cherrypy.quickstart(Root())
