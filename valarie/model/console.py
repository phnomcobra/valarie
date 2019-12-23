#!/usr/bin/python

from valarie.dao.document import Collection
from valarie.model.config import CONSOLE_PROTO_OBJUUID

def create_console(parent_objuuid, name = "New Console", objuuid = None):
    collection = Collection("inventory")
    console = collection.get_object(objuuid)
    console.object = {
        "type" : "console",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "body" : collection.get_object(CONSOLE_PROTO_OBJUUID).object["body"],
        "icon" : "/images/console_icon.png",
        "concurrency" : 1,
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/ajax_delete",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit console",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/ajax_copy_object",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            }
        }
    }
    
    console.set()
    
    parent = collection.get_object(parent_objuuid)
    parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
    parent.set()
    
    return console

def get_consoles():
    collection = Collection("inventory")
    
    console_objects = []
    
    for object in collection.find(type = "console"):
        console_objects.append(object.object)
        
    return console_objects