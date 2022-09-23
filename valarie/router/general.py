#!/usr/bin/python3
"""This module implements the restart route used for restarting valarie."""

from threading import Timer
from typing import Dict

import cherrypy

from valarie.controller.general import restart

class General(): # pylint: disable=too-few-public-methods
    """This class encapsulates the general purpose endpoints."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def restart(cls) -> Dict:
        """This function registers the route that restarts valarie."""
        Timer(3, restart).start()
        return {}
