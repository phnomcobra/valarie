#!/usr/bin/python3
"""This module implements the restart route used for restarting valarie."""

from threading import Timer

import cherrypy

from valarie.controller.general import restart
from valarie.router.messaging import add_message

class General(): # pylint: disable=too-few-public-methods
    """This class encapsulates the general purpose endpoints."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def restart(cls) -> dict:
        """This function registers the route that restarts valarie."""
        add_message("general controller: restarting in 3 seconds...")
        Timer(3, restart).start()
        return {}
