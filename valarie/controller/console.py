#!/usr/bin/python3
"""This module implements code for creating consoles and generating
lists of console objects used by the frontend for rendering."""

from typing import List

from valarie.dao.document import Collection, Object
from valarie.controller.config import get_console_template

def create_console(
        parent_objuuid: str,
        name: str = "New Console",
        objuuid: str = None
    ) -> Object:
    """This function creates and returns a console object in the inventory.

    Args:
        parent_objuuid:
            The UUID of this console's parent inventory object.

        name:
            The name of this console object.

        objuuid:
            The UUID for this console object.

    Returns:
        The document object for this console.
    """
    inventory = Collection("inventory")
    console = inventory.get_object(objuuid)
    console.object = {
        "type" : "console",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "body" : get_console_template(),
        "icon" : "/images/console_icon.png",
        "concurrency" : 1,
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/delete",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit console",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/copy_object",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            }
        }
    }

    console.set()

    parent = inventory.get_object(parent_objuuid)
    parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
    parent.set()

    return console

def get_consoles() -> List[Object]:
    """This function returns a list of all the console objects in the inventory.

    Returns:
        A list of document objects.
    """
    inventory = Collection("inventory")

    console_objects = []

    for console in inventory.find(type="console"):
        console_objects.append(console.object)

    return console_objects
