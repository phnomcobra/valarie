#!/usr/bin/python3
"""This module implements functions for creating and enumerating host groups."""

from valarie.dao.document import Collection
from valarie.router.messaging import add_message

def create_host_group(parent_objuuid: str, name: str = "New Host Group", objuuid: str = None):
    """This function creates and returns a host group object in the inventory.

    Args:
        parent_objuuid:
            The UUID of this controller's parent inventory object.

        name:
            The name of this host group object.

        objuuid:
            The UUID for this host group object.

    Returns:
        The document object for this host group.
    """
    inventory = Collection("inventory")

    group = inventory.get_object(objuuid)

    group.object = {
        "type" : "host group",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "hosts" : [],
        "icon" : "/images/host_group_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/delete",
                    "params" : {
                        "objuuid" : group.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit host group",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : group.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/copy_object",
                    "params" : {
                        "objuuid" : group.objuuid
                    }
                }
            }
        }
    }

    group.set()

    parent = inventory.get_object(parent_objuuid)
    parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
    parent.set()

    return group

def get_host_grid(grpuuid):
    """This function creates and returns a host group object in the inventory.

    Args:
        grpuuid:
            The UUID of the host group.

    Returns:
        A list of objects. Each object contains the type, name, host, and UUID for
        each host or nested host group. Nest hostgroups have the names joined with
        <br> HTML tags.
    """

    inventory = Collection("inventory")

    group = inventory.get_object(grpuuid)

    grid_data = []

    for hstuuid in group.object["hosts"]: # pylint: disable=too-many-nested-blocks
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
                    nested_host = inventory.get_object(uuid)

                    if "type" in nested_host.object:
                        if nested_host.object["type"] == "host":
                            hosts.append(
                                f'{nested_host.object["name"]} ({nested_host.object["host"]})'
                            )
                        elif nested_host.object["type"] == "host group":
                            hosts.append(nested_host.object["name"])
                    else:
                        host.object["hosts"].remove(uuid)
                        host.set()
                        nested_host.destroy()

                grid_data.append(
                    {
                        "type": host.object["type"],
                        "name": host.object["name"],
                        "host": str("<br>").join(hosts),
                        "objuuid": host.object["objuuid"]
                    }
                )
        else:
            add_message(f"host {hstuuid} is missing!")
            host.destroy()
            group.object["hosts"].remove(hstuuid)
            group.set()

    return grid_data
