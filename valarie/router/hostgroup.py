#!/usr/bin/python3
"""This module implements the host group routes."""

import cherrypy

from valarie.controller.hostgroup import get_host_grid

class HostGroup(): # pylint: disable=too-few-public-methods
    """This class registers the host group functions."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_host_grid(cls, objuuid: str) -> list:
        """This function registers the endpoint for retrieving summary data for
        each member of the host group. Members may be UUIDs for host or host
        group objects. This endpoint's response is used for populating host grid
        controls in the front end.

        Args:
            objuuid:
                The UUID of the hostgroup.

        Returns:
            JSON string of list of summary data objects.
        """
        return get_host_grid(objuuid)
