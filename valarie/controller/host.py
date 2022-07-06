#!/usr/bin/python3
"""This module implements code for creating hosts."""
from typing import List

from valarie.dao.document import Collection, Object

def create_host(
        parent_objuuid: str,
        name: str = "New Host",
        objuuid: str = None
    ) -> Object:
    """This function creates and returns a host object in the inventory.

    Args:
        parent_objuuid:
            The UUID of this host's parent inventory object.

        name:
            The name of this host object.

        objuuid:
            The UUID for this host object.

    Returns:
        The document object for this host.
    """
    inventory = Collection("inventory")

    host = inventory.get_object(objuuid)

    host.object = {
        "type" : "host",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "host" : "",
        "icon" : "/images/host_icon.png",
        "console" : None,
        "concurrency" : 1,
        "config" : "",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/delete",
                    "params" : {
                        "objuuid" : host.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit host",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : host.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/copy_object",
                    "params" : {
                        "objuuid" : host.objuuid
                    }
                }
            }
        }
    }

    host.set()

    parent = inventory.get_object(parent_objuuid)
    parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
    parent.set()

    return host

def get_hosts(
        hstuuid: str,
        hstuuids: List[str],
        grpuuids: List[str],
        inventory: Collection
    ):
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
    """
    current = inventory.get_object(hstuuid)

    if "type" in current.object: # pylint: disable=too-many-nested-blocks
        if current.object["type"] == "host":
            if hstuuid not in hstuuids:
                hstuuids.append(hstuuid)
        elif current.object["type"] == "host group":
            for uuid in current.object["hosts"]:
                nested = inventory.get_object(uuid)
                if "type" in nested.object:
                    if nested.object["type"] == "host group":
                        if uuid not in grpuuids:
                            grpuuids.append(uuid)
                            get_hosts(uuid, hstuuids, grpuuids, inventory)
                    elif nested.object["type"] == "host":
                        if uuid not in hstuuids:
                            hstuuids.append(uuid)
                else:
                    current.object["hosts"].remove(uuid)
                    current.set()
                    nested.destroy()
