#!/usr/bin/python3
"""This module implements functions for creating task objects, and retrieving
host grid data for the jsgrid controls in the frontend."""
from typing import Dict, List

from valarie.controller import logging
from valarie.controller.config import get_task_template
from valarie.dao.document import Collection, Object

def create_task(
        parent_objuuid: str,
        name: str = "New Task",
        objuuid: str = None
    ) -> Object:
    """This is a function used to create a task object in the inventory.

    Args:
        parent_objuuid:
            Parent object UUID.

        name:
            Name of the task object.

        objuuid:
            UUID of the task object.

    Returns:
        An inventory object.
    """
    inventory = Collection("inventory")

    task = inventory.get_object(objuuid)

    task.object = {
        "type" : "task",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "body" : get_task_template(),
        "hosts" : [],
        "icon" : "/images/task_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/delete",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit task",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            },
            "edit hosts" : {
                "label" : "Edit Hosts",
                "action" : {
                    "method" : "edit task hosts",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            },
            "run" : {
                "label" : "Run",
                "action" : {
                    "method" : "run task",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/copy_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            }
        }
    }

    task.set()

    parent = inventory.get_object(parent_objuuid)
    parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
    parent.set()

    return task

def get_host_grid(tskuuid: str) -> List[Dict]:
    """This is a function used to get a list of a task's hosts.

    Args:
        tskuuid:
            Task's object UUID.

    Returns:
        A list of dictionaries. Each dictionary contains a name,
        object UUID of the host, the host, and type.
    """
    inventory = Collection("inventory")

    task = inventory.get_object(tskuuid)

    grid_data = []

    for hstuuid in task.object["hosts"]:
        host = inventory.get_object(hstuuid)

        if "type" in host.object:
            if host.object["type"] == "host":
                grid_data.append(
                    {
                        "type": host.object["type"],
                        "name": host.object["name"],
                        "host": host.object["host"],
                        "objuuid": host.object["objuuid"]
                    }
                )
            elif host.object["type"] == "host group":
                hosts = []

                for uuid in host.object["hosts"]:
                    current = inventory.get_object(uuid)
                    if "name" in current.object:
                        hosts.append(current.object["name"])
                    else:
                        current.destroy()
                        host.object["hosts"].remove(uuid)
                        host.set()

                grid_data.append(
                    {
                        "type": host.object["type"],
                        "name": host.object["name"],
                        "host": str("<br>").join(hosts),
                        "objuuid": host.object["objuuid"]
                    }
                )
        else:
            logging.error(f"host {hstuuid} is missing!")
            host.destroy()
            task.object["hosts"].remove(hstuuid)
            task.set()

    return grid_data
