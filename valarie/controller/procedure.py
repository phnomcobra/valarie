#!/usr/bin/python3
"""This module implements functions for creating procedure objects, and retrieving
host and task grid data for the jsgrid controls in the frontend."""
from typing import Dict, List

from valarie.controller import logging
from valarie.dao.document import Collection, Object

def create_procedure(
        parent_objuuid: str,
        name: str = "New Procedure",
        objuuid: str = None
    ) -> Object:
    """This is a function used to create a procedure object in the inventory.

    Args:
        parent_objuuid:
            Parent object UUID.

        name:
            Name of the procedure object.

        objuuid:
            UUID of the procedure object.

    Returns:
        An inventory object.
    """
    inventory = Collection("inventory")

    procedure = inventory.get_object(objuuid)

    procedure.object = {
        "type": "procedure",
        "parent": parent_objuuid,
        "children": [],
        "name": name,
        "tasks": [],
        "title": "",
        "description": "",
        "resultexpirationperiod": 3600,
        "resultinventoryupdate": False,
        "resultoverwrite": True,
        "resultlinkenable": False,
        "enabled": False,
        "runasprocess": False,
        "seconds": "0",
        "minutes": "*",
        "hours": "*",
        "dayofmonth": "*",
        "dayofweek": "*",
        "year": "*",
        "rfcs": [],
        "hosts": [],
        "icon": "/images/procedure_icon.png",
        "context": {
            "delete": {
                "label": "Delete",
                "action": {
                    "method": "delete node",
                    "route": "inventory/delete",
                    "params": {
                        "objuuid": procedure.objuuid
                    }
                }
            },
            "edit": {
                "label": "Edit",
                "action": {
                    "method": "edit procedure",
                    "route": "inventory/get_object",
                    "params": {
                        "objuuid": procedure.objuuid
                    }
                }
            },
            "run": {
                "label": "Open",
                "action": {
                    "method": "run procedure",
                    "route": "inventory/get_object",
                    "params": {
                        "objuuid": procedure.objuuid
                    }
                }
            },
            "copy": {
                "label": "Copy",
                "action": {
                    "method": "copy node",
                    "route": "inventory/copy_object",
                    "params": {
                        "objuuid": procedure.objuuid
                    }
                }
            }
        }
    }

    procedure.set()

    parent = inventory.get_object(parent_objuuid)
    parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
    parent.set()

    return procedure

def get_task_grid(prcuuid: str) -> List[Dict]:
    """This is a function used to get a list of a procedure's tasks.

    Args:
        prcuuid:
            Procedure's object UUID.

    Returns:
        A list of dictionaries. Each dictionary contains a name, and
        object UUID of the task.
    """
    inventory = Collection("inventory")

    procedure = inventory.get_object(prcuuid)

    grid_data = []

    for tskuuid in procedure.object["tasks"]:
        task = inventory.get_object(tskuuid)

        if "type" in task.object:
            item = {
                "name": task.object["name"],
                "objuuid": task.object["objuuid"]
            }

            grid_data.append(item)
        else:
            logging.error("task {0} is missing!".format(tskuuid))

            item = {
                "name": "MISSING!",
                "objuuid": tskuuid
            }

            grid_data.append(item)

    return grid_data

def get_host_grid(prcuuid: str) -> List[Dict]:
    """This is a function used to get a list of a procedure's hosts.

    Args:
        prcuuid:
            Procedure's object UUID.

    Returns:
        A list of dictionaries. Each dictionary contains a name,
        object UUID of the host, the host, and type.
    """
    inventory = Collection("inventory")

    procedure = inventory.get_object(prcuuid)

    grid_data = []

    for hstuuid in procedure.object["hosts"]:
        host = inventory.get_object(hstuuid)

        if "type" in host.object:
            if host.object["type"] == "host":
                item = {
                    "type": host.object["type"],
                    "name": host.object["name"],
                    "host": host.object["host"],
                    "objuuid": host.object["objuuid"]
                }

                grid_data.append(item)
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

                item = {
                    "type": host.object["type"],
                    "name": host.object["name"],
                    "host": str("<br>").join(hosts),
                    "objuuid": host.object["objuuid"]
                }

                grid_data.append(item)
        else:
            logging.error(f"host {hstuuid} is missing!")
            host.destroy()
            procedure.object["hosts"].remove(hstuuid)
            procedure.set()

    return grid_data
