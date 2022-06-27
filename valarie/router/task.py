#!/usr/bin/python3
"""This module implements routes for getting a task's host grid,
and executing the task."""
from typing import Dict, List

import cherrypy

from valarie.controller.task import get_host_grid
from valarie.executor.task import execute

class Task():
    """This class registers methods as routes for getting a task's
    host grid, and executing the task."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_host_grid(cls, objuuid: str) -> List[Dict]:
        """This function registers the endpoint that returns a task's
        list of hosts.

        Args:
            objuuid:
                A task's UUID.

        Returns:
            A list of host items for jsgrid.
        """
        get_host_grid(objuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def execute_task(cls, tskuuid: str, hstuuid: str) -> List[Dict]:
        """This function registers the endpoint that executes a task and
        returns task's result.

        Args:
            tskuuid:
                A task's UUID.

            hstuuid:
                A host's UUID.

        Returns:
            A list of host items for jsgrid.
        """
        execute(tskuuid, hstuuid)
