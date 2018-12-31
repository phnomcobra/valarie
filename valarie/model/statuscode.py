#!/usr/bin/python

from valarie.dao.document import Collection

def get_status_objects():
    collection = Collection("inventory")
    
    status_objects = []
    
    for object in collection.find(type = "status"):
        status_objects.append(object.object)
        
    return status_objects

def create_status_code(parent_objuuid, name = "New Status Code", objuuid = None):
    collection = Collection("inventory")
    
    status = collection.get_object(objuuid)
    
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
                    "route" : "inventory/ajax_delete",
                    "params" : {
                        "objuuid" : status.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit status code",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : status.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/ajax_copy_object",
                    "params" : {
                        "objuuid" : status.objuuid
                    }
                }
            }
        }
    }
    
    status.set()
    
    parent = collection.get_object(parent_objuuid)
    parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
    parent.set()
    
    return status