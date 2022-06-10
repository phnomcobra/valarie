#!/usr/bin/python3

import cherrypy

from valarie.view.index import index_view

from valarie.router.inventory import Inventory
from valarie.router.messaging import Messaging
from valarie.router.hostgroup import HostGroup
from valarie.router.procedure import Procedure
from valarie.router.controller import Controller
from valarie.router.console import Console
from valarie.router.results import Results
from valarie.router.flags import Flags
from valarie.router.task import Task
from valarie.router.general import General

class Root(object):
    inventory = Inventory()
    messaging = Messaging()
    procedure = Procedure()
    controller = Controller()
    console = Console()
    results = Results()
    flags = Flags()
    task = Task()
    hostgroup = HostGroup()
    general = General()

    @cherrypy.expose
    def index(self):
        return index_view()
