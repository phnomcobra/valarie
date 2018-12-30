#!/usr/bin/python

from valarie.dao.document import Collection
from valarie.controller.messaging import add_message

def create_host_group(parent_objuuid, name = "New Host Group", objuuid = None):
    collection = Collection("inventory")

    group = collection.get_object(objuuid)

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
                    "route" : "inventory/ajax_delete",
                    "params" : {
                        "objuuid" : group.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit host group",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : group.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/ajax_copy_object",
                    "params" : {
                        "objuuid" : group.objuuid
                    }
                }
            }
        }
    }
    
    group.set()
    
    parent = collection.get_object(parent_objuuid)
    parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
    parent.set()
    
    return group

def get_host_grid(grpuuid):
    collection = Collection("inventory")
    
    group = collection.get_object(grpuuid)
    
    grid_data = []
    
    for hstuuid in group.object["hosts"]:
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
                    h = collection.get_object(uuid)
                    
                    if "type" in h.object:
                        if h.object["type"] == "host":
                            hosts.append("{0} ({1})".format(h.object["name"], \
                                                            h.object["host"]))
                        elif h.object["type"] == "host group":
                            hosts.append(h.object["name"])
                    else:
                        host.object["hosts"].remove(uuid)
                        host.set()
                        h.destroy()
                        
                
                grid_data.append({"type" : host.object["type"], \
                                  "name" : host.object["name"], \
                                  "host" : str("<br>").join(hosts), \
                                  "objuuid" : host.object["objuuid"]})
        else:
            add_message("host {0} is missing!".format(hstuuid))
            host.destroy()
            group.object["hosts"].remove(hstuuid)
            group.set()
        
    return grid_data