#!/usr/bin/python3

from valarie.dao.document import Collection

def create_container(parent_objuuid, name = "New Container", objuuid = None):
    collection = Collection("inventory")
    
    container = collection.get_object(objuuid)
    
    container.object = {
        "type" : "container",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "context" : {
            "new container" : {
                "label" : "New Container",
                "action" : {
                    "method" : "create container",
                    "route" : "inventory/create_container",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "new task" : {
                "label" : "New Task",
                "action" : {
                    "method" : "create task",
                    "route" : "inventory/create_task",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "new text file" : {
                "label" : "New Text File",
                "action" : {
                    "method" : "create text file",
                    "route" : "inventory/create_text_file",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "new procedure" : {
                "label" : "New Procedure",
                "action" : {
                    "method" : "create procedure",
                    "route" : "inventory/create_procedure",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "new controller" : {
                "label" : "New Controller",
                "action" : {
                    "method" : "create controller",
                    "route" : "inventory/create_controller",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "new status" : {
                "label" : "New Status Code",
                "action" : {
                    "method" : "create status",
                    "route" : "inventory/create_status_code",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "new host" : {
                "label" : "New Host",
                "action" : {
                    "method" : "create host",
                    "route" : "inventory/create_host",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "new host group" : {
                "label" : "New Host Group",
                "action" : {
                    "method" : "create host group",
                    "route" : "inventory/create_host_group",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "new console" : {
                "label" : "New Console",
                "action" : {
                    "method" : "create console",
                    "route" : "inventory/create_console",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/delete",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit container",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/copy_object",
                    "params" : {
                        "objuuid" : container.objuuid
                    }
                }
            }
        }
    }
    
    container.set()
    
    if parent_objuuid == "#":
        container.object["icon"] = "images/tree_icon.png"
    else:
        parent = collection.get_object(parent_objuuid)
        parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
        parent.set()
    
    return container
