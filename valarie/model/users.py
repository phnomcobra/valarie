#!/usr/bin/python

from valarie.dao.document import Collection

USERS_CONTAINER_OBJUUID = "04260c4f-a624-445b-99f5-eb079f08eb16"

def create_user(objuuid = None, name = "New User"):
    collection = Collection("inventory")

    user = collection.get_object(objuuid)

    user.object = {
        "type" : "user",
        "parent" : USERS_CONTAINER_OBJUUID,
        "children" : [],
        "name" : name,
        "password" : "",
        "enabled" : False,
        "sessionid" : "",
        "icon" : "/images/user_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/ajax_delete",
                    "params" : {
                        "objuuid" : user.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit user",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : user.objuuid
                    }
                }
            }
        }
    }
    
    user.set()
    
    parent = collection.get_object(USERS_CONTAINER_OBJUUID)
    parent.object["children"] = collection.find_objuuids(parent=USERS_CONTAINER_OBJUUID)
    parent.set()
    
    return user

def create_users_container():
    collection = Collection("inventory")
    
    container = collection.get_object(USERS_CONTAINER_OBJUUID)
    
    container.object = {
        "type" : "container",
        "parent" : "#",
        "children" : [],
        "name" : "Users",
        "icon" : "images/tree_icon.png",
        "context" : {
            "new user" : {
                "label" : "New User",
                "action" : {
                    "method" : "create user",
                    "route" : "inventory/ajax_create_user",
                    "params" : {}
                }
            }
        }
    }
    
    container.set()
    
    return container
