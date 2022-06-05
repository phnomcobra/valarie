#!/usr/bin/python

import cherrypy

from valarie.view.index import index_view

from valarie.controller.inventory import Inventory
from valarie.controller.messaging import Messaging
from valarie.controller.hostgroup import HostGroup
from valarie.controller.procedure import Procedure
from valarie.controller.controller import Controller
from valarie.controller.console import Console
from valarie.controller.results import Results
from valarie.controller.flags import Flags
from valarie.controller.task import Task
from valarie.controller.general import General

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
