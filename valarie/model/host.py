#!/usr/bin/python

from valarie.dao.document import Collection

def create_host(parent_objuuid, name = "New Host", objuuid = None):
    collection = Collection("inventory")

    host = collection.get_object(objuuid)

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
    
    parent = collection.get_object(parent_objuuid)
    parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
    parent.set()
    
    return host
