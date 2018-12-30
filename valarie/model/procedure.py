#!/usr/bin/python

from valarie.dao.document import Collection
from valarie.controller.messaging import add_message

def create_procedure(parent_objuuid, name = "New Procedure", objuuid = None):
    collection = Collection("inventory")
    
    procedure = collection.get_object(objuuid)
    
    procedure.object = {
        "type" : "procedure",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "tasks" : [],
        "title" : "",
        "description" : "",
        "enabled" : False,
        "minutes" : "*",
        "hours" : "*",
        "dayofmonth" : "*",
        "dayofweek" : "*",
        "year" : "*",
        "rfcs" : [],
        "hosts" : [],
        "icon" : "/images/procedure_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/ajax_delete",
                    "params" : {
                        "objuuid" : procedure.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit procedure",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : procedure.objuuid
                    }
                }
            },
            "run" : {
                "label" : "Open",
                "action" : {
                    "method" : "run procedure",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : procedure.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/ajax_copy_object",
                    "params" : {
                        "objuuid" : procedure.objuuid
                    }
                }
            }
        }
    }
    
    procedure.set()
    
    parent = collection.get_object(parent_objuuid)
    parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
    parent.set()
    
    return procedure

def get_task_grid(prcuuid):
    collection = Collection("inventory")
    
    procedure = collection.get_object(prcuuid)
    
    grid_data = []
    
    for tskuuid in procedure.object["tasks"]:
        task = collection.get_object(tskuuid)
        
        if "type" in task.object:
            item = {
                "name" : task.object["name"], 
                "objuuid" : task.object["objuuid"]
            }
            
            grid_data.append(item)
        else:
            add_message("task {0} is missing!".format(tskuuid))
            
            item = {
                "name" : "MISSING!",
                "objuuid" : tskuuid
            }
            
            grid_data.append(item)
        
    return grid_data

def get_host_grid(prcuuid):
    collection = Collection("inventory")
    
    procedure = collection.get_object(prcuuid)
    
    grid_data = []
    
    for hstuuid in procedure.object["hosts"]:
        host = collection.get_object(hstuuid)
        
        if "type" in host.object:
            if host.object["type"] == "host":
                item = {
                    "type" : host.object["type"],
                    "name" : host.object["name"],
                    "host" : host.object["host"],
                    "objuuid" : host.object["objuuid"]
                }
                                  
                grid_data.append(item)
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
                
                item = {
                    "type" : host.object["type"],
                    "name" : host.object["name"],
                    "host" : str("<br>").join(hosts),
                    "objuuid" : host.object["objuuid"]
                }
                
                grid_data.append(item)
        else:
            add_message("host {0} is missing!".format(hstuuid))
            host.destroy()
            procedure.object["hosts"].remove(hstuuid)
            procedure.set()
        
    return grid_data