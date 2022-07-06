#!/usr/bin/python3
"""This module implements functions and classes for synchronously executing tasks."""
import traceback
from typing import Any, Dict
from imp import new_module
from time import time

from valarie.dao.document import Collection
from valarie.router.messaging import add_message

class TaskError: # pylint: disable=too-few-public-methods
    """The class is used to encapsulate errors as Task objects."""
    def __init__(self, uuid: str):
        """The TaskError's contructor.

        Args:
            uuid:
                A task object's UUID.
        """
        self.output = ['<font color="red">'] + traceback.format_exc().split("\n") + ["</font>"]
        self.uuid = uuid
        self.status = 5

    def execute(self, cli: Any) -> int: # pylint: disable=unused-argument
        """This function exists to maintain the interface of an ordinary Task
        object.

        Args:
            cli:
                A console object. This is not used for task errors so it can
                be anything.
        """
        return self.status

def execute(tskuuid: str, hstuuid: str) -> Dict:
    """This is a function used to run a task and return its result.

    Args:
        tskuuid:
            UUID of the task object.

        hstuuid:
            UUID of the host object.

    Returns:
        A dictionary of the result.
    """
    inventory = Collection("inventory")
    results = Collection("results")

    for result in results.find(hstuuid=hstuuid, tskuuid=tskuuid):
        result.destroy()

    result = results.get_object()

    result.object['start'] = time()

    status_code_body = ""
    status_data = {}

    for status in inventory.find(type="status"):
        try:
            status_code_body += f"""{status.object["alias"]}=int('{status.object["code"]}')\n"""
            status_data[int(status.object["code"])] = status.object
        except (KeyError, ValueError) as exception:
            add_message(str(exception))

    host = inventory.get_object(hstuuid)
    result.object['host'] = {}
    result.object['host']['host'] = host.object['host']
    result.object['host']['name'] = host.object['name']
    result.object['host']['objuuid'] = hstuuid

    tempmodule = new_module("tempmodule")

    try:
        # pylint: disable=exec-used
        exec(inventory.get_object(host.object["console"]).object["body"], tempmodule.__dict__)
        cli = tempmodule.Console(host=host.object)

        try:
            inv_task = inventory.get_object(tskuuid)

            result.object['task'] = {}
            result.object['task']["name"] = inv_task.object["name"]
            result.object['task']["start"] = None
            result.object['task']["stop"] = None
            result.object['task']["tskuuid"] = tskuuid

            # pylint: disable=exec-used
            exec(f'{inv_task.object["body"]}\n{status_code_body}', tempmodule.__dict__)
            task = tempmodule.Task()

            try:
                task.execute(cli)
            except: # pylint: disable=bare-except
                task = TaskError(tskuuid)
                add_message(traceback.format_exc())
        except: # pylint: disable=bare-except
            task = TaskError(tskuuid)
            add_message(traceback.format_exc())
    except: # pylint: disable=bare-except
        task = TaskError(tskuuid)
        add_message(traceback.format_exc())

    result.object['output'] = task.output

    try:
        result.object['status'] = status_data[task.status]
    except KeyError as exception:
        add_message(str(exception))
        result.object['status'] = {"code": task.status}

    result.object['stop'] = time()
    result.set()

    return result.object
