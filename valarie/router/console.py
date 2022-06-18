#!/usr/bin/python3
"""This module implements the console routes."""

from typing import List

import cherrypy

from valarie.controller.console import get_consoles
from valarie.dao.document import Object

class Console(): # pylint: disable=too-few-public-methods
    """This class encapsulates the console routes."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_consoles(cls) -> List[Object]:
        """This function returns a list of console objects used in
        the frontend for populating the console radio button control in host attributes.

        Returns:
            JSON string of consoles.
        """
        return get_consoles()
