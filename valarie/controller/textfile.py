#!/usr/bin/python3
"""This module implements functions for creating text file inventory objects."""
from valarie.dao.document import Collection, Object

def create_text_file(
        parent_objuuid: str,
        name: str = "New Text File",
        objuuid: str = None
    ) -> Object:
    """This is a function used to create a text file object in the inventory.

    Args:
        parent_objuuid:
            Parent object UUID.

        name:
            Name of the text file object.

        objuuid:
            UUID of the text file object.

    Returns:
        An inventory object.
    """
    inventory = Collection("inventory")

    text_file = inventory.get_object(objuuid)

    text_file.object = {
        "type" : "text file",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "body" : "",
        "language" : "plain_text",
        "icon" : "/images/text_file_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/delete",
                    "params" : {
                        "objuuid" : text_file.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit text file",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : text_file.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/copy_object",
                    "params" : {
                        "objuuid" : text_file.objuuid
                    }
                }
            }
        }
    }

    text_file.set()

    if parent_objuuid != "#":
        parent = inventory.get_object(parent_objuuid)
        parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
        parent.set()

    return text_file
