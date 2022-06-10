#!/usr/bin/python3
"""This module implements the console routes."""

import json

import cherrypy

from valarie.controller.console import get_consoles

class Console(): # pylint: disable=too-few-public-methods
    """This class encapsulates the console routes."""
    @classmethod
    @cherrypy.expose
    def get_consoles(cls) -> str:
        """This function returns a list of console objects used in
        the frontend for populating the console radio button control in host attributes.

        Returns:
            JSON string of consoles.
        """
        return json.dumps(get_consoles())
