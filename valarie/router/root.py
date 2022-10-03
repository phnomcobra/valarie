#!/usr/bin/python3
"""This module mounts the static index endpoint and registers the
various cherrypy classes into the root of the application."""
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

class Root(): # pylint: disable=too-few-public-methods
    """This class mounts the static index endpoint and registers the
    various cherrypy classes into the root of the application."""
    inventory = Inventory()
    messaging = Messaging()
    procedure = Procedure()
    controller = Controller()
    console = Console()
    results = Results()
    flags = Flags()
    task = Task()
    hostgroup = HostGroup()

    @classmethod
    @cherrypy.expose
    def index(cls) -> str:
        """This function registers the endpoint that retrieves the
        index page.

        Returns:
            An HTML string.
        """
        return index_view()
