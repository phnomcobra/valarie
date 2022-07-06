#!/usr/bin/python3
"""This module implements functions for getting and creating status
code objects."""
from typing import Dict, List

from valarie.dao.document import Collection, Object

def get_status_objects() -> List[Dict]:
    """This function returns all of the status objects.

    Returns:
        List of inventory object dictionaries."""
    inventory = Collection("inventory")

    status_objects = []

    for status in inventory.find(type="status"):
        status_objects.append(status.object)

    return status_objects

def create_status_code(
        parent_objuuid: str,
        name: str = "New Status Code",
        objuuid: str = None
    ) -> Object:
    """This is a function used to create a status code object in the inventory.

    Args:
        parent_objuuid:
            Parent object UUID.

        name:
            Name of the status code object.

        objuuid:
            UUID of the status code object.

    Returns:
        An inventory object.
    """
    inventory = Collection("inventory")

    status = inventory.get_object(objuuid)

    status.object = {
        "type" : "status",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "alias" : "STATUS_{0}".format(str(name).upper()),
        "code" : 0,
        "abbreviation" : name,
        "cfg" : "000000",
        "cbg" : "FFFFFF",
        "sfg" : "000000",
        "sbg" : "999999",
        "icon" : "/images/status_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/delete",
                    "params" : {
                        "objuuid" : status.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit status code",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : status.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/copy_object",
                    "params" : {
                        "objuuid" : status.objuuid
                    }
                }
            }
        }
    }

    status.set()

    parent = inventory.get_object(parent_objuuid)
    parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
    parent.set()

    return status
