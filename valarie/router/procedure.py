#!/usr/bin/python3
"""This module implements the routes for getting a procedure's task and
host grids, queuing single and multiple procedures, and getting the queue
grid."""

from typing import Dict, List

import cherrypy

from valarie.controller.procedure import get_task_grid, get_host_grid
from valarie.executor.procedure import (
    get_jobs_grid,
    queue_procedure,
    cancel_job
)

class Procedure():
    """This class registers methods as routes for getting a procedure's
    task and host grids, queuing single and multiple procedures, and
    getting the queue grid."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_task_grid(cls, objuuid: str) -> List[Dict]:
        """This function registers the endpoint that returns a procedure's
        list of tasks.

        Args:
            objuuid:
                A procedure's UUID.

        Returns:
            A list of task items for jsgrid.
        """
        return get_task_grid(objuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_host_grid(cls, objuuid: str) -> List[Dict]:
        """This function registers the endpoint that returns a procedure's
        list of hosts.

        Args:
            objuuid:
                A procedure's UUID.

        Returns:
            A list of host items for jsgrid.
        """
        return get_host_grid(objuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def queue_procedure(cls, prcuuid: str, hstuuid: str) -> Dict:
        """This function registers the endpoint that queues a procedure
        for execution for a specified host.

        Args:
            prcuuid:
                A procedure's UUID.

            hstuuid:
                A host's UUID.
        """
        queue_procedure(hstuuid, prcuuid)
        return {}

    @classmethod
    @cherrypy.expose
    def cancel_job(cls, jobuuid: str):
        """This function registers the endpoint that cancels a procedure's
        job in the queue..

        Args:
            jobuuid:
                A job UUID.
        """
        cancel_job(jobuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_in()
    @cherrypy.tools.json_out()
    def queue_procedures(cls) -> List[Dict]:
        """This function registers the endpoint that queues multiple
        procedures execution.

        Returns:
            A list of dictionaries where each contains a host UUID,
            procedure UUID, and optionally a controller UUID.
        """
        queuelist = cherrypy.request.json
        for item in queuelist:
            if "ctruuid" in item:
                ctruuid = item["ctruuid"]
            else:
                ctruuid = None
            queue_procedure(item["hstuuid"], item["prcuuid"], ctruuid)
        return queuelist

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_queue_grid(cls) -> List[Dict]:
        """This function registers the endpoint that returns the queued
        and running procedures.

        Returns:
            A list of queue items.
        """
        return get_jobs_grid()
