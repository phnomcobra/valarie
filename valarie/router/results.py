#!/usr/bin/python3
"""This module implements the routes for getting result objects for
controller, procedures, and result UUIDs."""
from typing import List, Dict

import cherrypy

from valarie.controller.results import (
    get_controller_results,
    get_procedure_result,
    get_result
)

class Results():
    """This class registers methods as routes for getting result
    objects for controller, procedures, and result UUIDs."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_controller(cls, objuuid: str) -> List[Dict]:
        """This function registers the endpoint that retrieves a
        list of results for a controller.

        Args:
            objuuid:
                A controller's UUID.

        Returns:
            A list of result objects.
        """
        return get_controller_results(objuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_procedure(cls, prcuuid: str, hstuuid: str) -> List[Dict]:
        """This function registers the endpoint that retrieves a
        list of results for a procedure. When retrieving a result in
        this mode, the UUIDs of the procedure and the host it was
        executed upon are required.

        Args:
            prcuuid:
                A procedure's UUID.

            hstuuid:
                A host's UUID.

        Returns:
            A list of result objects.
        """
        return get_procedure_result(prcuuid, hstuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_result(cls, resuuid: str) -> List[Dict]:
        """This function registers the endpoint that retrieves a
        list of results for a known result UUID.

        Args:
            resuuid:
                A result's UUID.

        Returns:
            A list of result objects.
        """
        return get_result(resuuid)
