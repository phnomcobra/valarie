#!/usr/bin/python3
"""This module implements code for creating controllers and generating
lists of hosts and procedure objects used by the frontend for rendering."""
from typing import Dict, List

from valarie.dao.document import Collection, Object
from valarie.controller.host import get_hosts
from valarie.controller import logging

def create_controller(
        parent_objuuid: str,
        name: str = "New Controller",
        objuuid: str = None
    ) -> Object:
    """This function creates and returns a controller object in the inventory.

    Args:
        parent_objuuid:
            The UUID of this controller's parent inventory object.

        name:
            The name of this controller object.

        objuuid:
            The UUID for this controller object.

    Returns:
        The document object for this controller.
    """

    inventory = Collection("inventory")

    controller = inventory.get_object(objuuid)

    controller.object = {
        "type" : "controller",
        "parent" : parent_objuuid,
        "children" : [],
        "hosts" : [],
        "procedures" : [],
        "name" : name,
        "icon" : "/images/controller_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/delete",
                    "params" : {
                        "objuuid" : controller.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit controller",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : controller.objuuid
                    }
                }
            },
            "run" : {
                "label" : "Open",
                "action" : {
                    "method" : "run controller",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : controller.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/copy_object",
                    "params" : {
                        "objuuid" : controller.objuuid
                    }
                }
            }
        }
    }

    controller.set()

    parent = inventory.get_object(parent_objuuid)
    parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
    parent.set()

    return controller

def get_procedure_grid(ctruuid: str) -> List[Dict]:
    """This function returns a list of the controller's procedures.

    A list of dictionaries is returned.
    Each dictionary contains the name, type, and UUID of a procedure.

    Args:
        objuuid:
            The UUID for this controller object.

    Returns:
        List of dictionaries.
    """
    inventory = Collection("inventory")

    controller = inventory.get_object(ctruuid)

    grid_data = []

    for prcuuid in controller.object["procedures"]:
        procedure = inventory.get_object(prcuuid)

        if "type" in procedure.object:
            grid_data.append({
                "name" : procedure.object["name"],
                "objuuid" : procedure.object["objuuid"],
                "type" : procedure.object["type"]
            })
        else:
            logging.error("procedure {0} is missing!".format(prcuuid))
            grid_data.append({
                "name" : "MISSING!",
                "objuuid" : prcuuid,
                "type" : "void"
            })

    return grid_data

def get_host_grid(ctruuid: str) -> List[Dict]:
    """This function returns a list of the controller's hosts.

    A list of dictionaries is returned.
    Each dictionary contains the name, type, host, and UUID of a host.

    Args:
        objuuid:
            The UUID for this controller object.

    Returns:
        List of dictionaries.
    """
    inventory = Collection("inventory")

    controller = inventory.get_object(ctruuid)

    grid_data = []

    for hstuuid in controller.object["hosts"]:
        host = inventory.get_object(hstuuid)

        if "type" in host.object:
            if host.object["type"] == "host":
                grid_data.append(
                    {
                        "type" : host.object["type"],
                        "name" : host.object["name"],
                        "host" : host.object["host"],
                        "objuuid" : host.object["objuuid"]
                    }
                )
            elif host.object["type"] == "host group":
                hosts = []

                for uuid in host.object["hosts"]:
                    member_host = inventory.get_object(uuid)
                    if "name" in member_host.object:
                        hosts.append(member_host.object["name"])
                    else:
                        host.object["hosts"].remove(uuid)
                        host.set()
                        member_host.destroy()

                grid_data.append(
                    {
                        "type" : host.object["type"],
                        "name" : host.object["name"],
                        "host" : str("<br>").join(hosts),
                        "objuuid" : host.object["objuuid"]
                    }
                )
        else:
            logging.error("host {0} is missing!".format(hstuuid))
            host.destroy()
            controller.object["hosts"].remove(hstuuid)
            controller.set()

    return grid_data

def get_tiles(ctruuid: str) -> dict:
    """This function returns a list of host and procedure UUIDs.

    The returned lists are used to assemble a grid of
    host/procedure intersections in the frontend.

    Args:
        ctruuid:
            The controller's UUID.

    Returns:
        Dictionary containing lists of procedure and host UUIDs.
    """
    inventory = Collection("inventory")

    controller = inventory.get_object(ctruuid)

    procedures = []
    for prcuuid in controller.object["procedures"]:
        procedures.append(inventory.get_object(prcuuid).object)

    hstuuids = []
    grpuuids = []

    for hstuuid in controller.object["hosts"]:
        get_hosts(hstuuid, hstuuids, grpuuids, inventory)

    hosts = []
    for hstuuid in hstuuids:
        hosts.append(inventory.get_object(hstuuid).object)

    return {"hosts" : hosts, "procedures" : procedures}
