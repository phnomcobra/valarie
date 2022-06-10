#!/usr/bin/python3
"""This module implements code for creating controllers and generating
lists of hosts and procedure objects used by the frontend for rendering."""

from typing import Dict
from typing import List

from valarie.dao.document import Collection
from valarie.dao.document import Object
from valarie.router.messaging import add_message

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
    collection = Collection("inventory")

    controller = collection.get_object(ctruuid)

    grid_data = []

    for prcuuid in controller.object["procedures"]:
        procedure = collection.get_object(prcuuid)

        if "type" in procedure.object:
            grid_data.append({
                "name" : procedure.object["name"],
                "objuuid" : procedure.object["objuuid"],
                "type" : procedure.object["type"]
            })
        else:
            add_message("procedure {0} is missing!".format(prcuuid))
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
    collection = Collection("inventory")

    controller = collection.get_object(ctruuid)

    grid_data = []

    for hstuuid in controller.object["hosts"]:
        host = collection.get_object(hstuuid)

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
                    member_host = collection.get_object(uuid)
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
            add_message("host {0} is missing!".format(hstuuid))
            host.destroy()
            controller.object["hosts"].remove(hstuuid)
            controller.set()

    return grid_data

def get_hosts(hstuuid: str, hstuuids: List[str], grpuuids: List[str], inventory: Collection):
    """This function accumulates associated host and host group UUIDs.

    This is a recursive function that is used to resolve a list of host UUIDs.
    In the event that a host UUID is referencing a host group;
    and by extension, a UUID in a host group is referencing another host group(s);
    this recursion function traverses the inventory and accumulates host and host group UUIDs.

    Args:
        hstuuid:
            The initial UUID to begin traversing the inventory from.

        hstuuids:
            List of host UUIDs.

        grpuuids:
            List of host group UUIDs.

        inventory:
            Document collection of the inventory.
    """
    o = inventory.get_object(hstuuid) # pylint: disable=invalid-name

    if "type" in o.object: # pylint: disable=too-many-nested-blocks
        if o.object["type"] == "host":
            if hstuuid not in hstuuids:
                hstuuids.append(hstuuid)
        elif o.object["type"] == "host group":
            for uuid in o.object["hosts"]:
                c = inventory.get_object(uuid) # pylint: disable=invalid-name
                if "type" in c.object:
                    if c.object["type"] == "host group":
                        if uuid not in grpuuids:
                            grpuuids.append(uuid)
                            get_hosts(uuid, hstuuids, grpuuids, inventory)
                    elif c.object["type"] == "host":
                        if uuid not in hstuuids:
                            hstuuids.append(uuid)
                else:
                    o.object["hosts"].remove(uuid)
                    o.set()
                    c.destroy()

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
    collection = Collection("inventory")

    controller = collection.get_object(ctruuid)

    procedures = []
    for prcuuid in controller.object["procedures"]:
        procedures.append(collection.get_object(prcuuid).object)

    hstuuids = []
    grpuuids = []

    for hstuuid in controller.object["hosts"]:
        get_hosts(hstuuid, hstuuids, grpuuids, collection)

    hosts = []
    for hstuuid in hstuuids:
        hosts.append(collection.get_object(hstuuid).object)

    return {"hosts" : hosts, "procedures" : procedures}
