#!/usr/bin/python

from valarie.dao.document import Collection
from valarie.controller.messaging import add_message
from valarie.model.config import get_task_template

def create_task(parent_objuuid, \
                name = "New Task", \
                objuuid = None, \
                author = "<author>", \
                email = "<email>", \
                phone = "<phone>"):
    collection = Collection("inventory")
    
    task = collection.get_object(objuuid)
    
    task.object = {
        "type" : "task",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "body" : get_task_template(),
        "hosts" : [],
        "icon" : "/images/task_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/ajax_delete",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit task",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            },
            "edit hosts" : {
                "label" : "Edit Hosts",
                "action" : {
                    "method" : "edit task hosts",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            },
            "run" : {
                "label" : "Run",
                "action" : {
                    "method" : "run task",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/ajax_copy_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            }
        }
    }
    
    task.set()
    
    parent = collection.get_object(parent_objuuid)
    parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
    parent.set()
    
    return task

def get_host_grid(tskuuid):
    collection = Collection("inventory")
    
    task = collection.get_object(tskuuid)
    
    grid_data = []
    
    for hstuuid in task.object["hosts"]:
        host = collection.get_object(hstuuid)
        
        if "type" in host.object:
            if host.object["type"] == "host":
                grid_data.append({"type" : host.object["type"], \
                                  "name" : host.object["name"], \
                                  "host" : host.object["host"], \
                                  "objuuid" : host.object["objuuid"]})
            elif host.object["type"] == "host group":
                hosts = []
                
                for uuid in host.object["hosts"]:
                    c = collection.get_object(uuid)
                    if "name" in c.object:
                        hosts.append(c.object["name"])
                    else:
                        c.destroy()
                        host.object["hosts"].remove(uuid)
                        host.set()
                
                grid_data.append({"type" : host.object["type"], \
                                  "name" : host.object["name"], \
                                  "host" : str("<br>").join(hosts), \
                                  "objuuid" : host.object["objuuid"]})
        else:
            add_message("host {0} is missing!".format(hstuuid))
            host.destroy()
            task.object["hosts"].remove(hstuuid)
            task.set()
        
    return grid_data