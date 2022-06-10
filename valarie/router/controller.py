#!/usr/bin/python3
"""This module implements the controller routes."""

import json

import cherrypy

from valarie.controller.controller import (
    get_procedure_grid,
    get_host_grid,
    get_tiles
)

class Controller():
    """This class encapsulates the controller routes."""
    @classmethod
    @cherrypy.expose
    def get_procedure_grid(cls, objuuid: str) -> str:
        """This function returns a list of procedure dictionaries.
        Each dictionary contains a type, name, and UUID.

        Args:
            objuuid:
                The UUID of the controller.

        Returns:
            JSON string of procedures.
        """
        return json.dumps(get_procedure_grid(objuuid))

    @classmethod
    @cherrypy.expose
    def get_host_grid(cls, objuuid: str) -> str:
        """This function returns a list of host dictionaries.
        Each dictionary contains a type, name, host, and UUID.

        Args:
            objuuid:
                The UUID of the controller.

        Returns:
            JSON string of hosts.
        """
        return json.dumps(get_host_grid(objuuid))

    @classmethod
    @cherrypy.expose
    def get_tiles(cls, objuuid: str) -> str:
        """This function returns a dictionary consisting of a
        list of host objects and procedure objects.

        Args:
            objuuid:
                The UUID of the controller.

        Returns:
            JSON string of hosts and procedures.
        """
        return json.dumps(get_tiles(objuuid))
