#!/usr/bin/python

from valarie.dao.document import Collection

def create_text_file(parent_objuuid, name = "New Text File", objuuid = None):
    collection = Collection("inventory")
    
    text_file = collection.get_object(objuuid)
    
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
        parent = collection.get_object(parent_objuuid)
        parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
        parent.set()
    
    return text_file
