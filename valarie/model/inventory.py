#!/usr/bin/python

import traceback

from valarie.dao.document import Collection
from valarie.model.datastore import delete_sequence, copy_sequence
from valarie.model.container import create_container
from valarie.controller.messaging import add_message
from valarie.controller.flags import touch_flag
from valarie.model.config import (
    CONFIG_OBJUUID,
    TASK_PROTO_OBJUUID,
    CONSOLE_PROTO_OBJUUID,
    PUBLIC_KEY_OBJUUID,
    PRIVATE_KEY_OBJUUID,
    SETTINGS_CONTAINER_OBJUUID,
    create_config,
    create_console_template,
    create_task_template,
    create_public_key,
    create_private_key,
    create_settings_container
)
from valarie.model.users import (
    create_user,
    create_users_container,
    USERS_CONTAINER_OBJUUID
)

FIXED_OBJUUIDS = (
    CONFIG_OBJUUID,
    TASK_PROTO_OBJUUID,
    CONSOLE_PROTO_OBJUUID,
    PUBLIC_KEY_OBJUUID,
    PRIVATE_KEY_OBJUUID,
    SETTINGS_CONTAINER_OBJUUID,
    USERS_CONTAINER_OBJUUID
) 

def __get_child_nodes(nodes, object, collection):
    try:
        node = {
            "id" : object.objuuid, 
            "parent" : object.object["parent"], 
            "text" : object.object["name"],
            "type" : object.object["type"]
        }
    
        if "icon" in object.object:
            node["icon"] = object.object["icon"]
    
        nodes.append(node)

        for objuuid in collection.find_objuuids(parent = object.objuuid):
            nodes = __get_child_nodes(nodes, collection.get_object(objuuid), collection)
    except:
        print(traceback.format_exc())
        print(object.object)
 
    return nodes
    
def get_child_nodes(objuuid):
    nodes = []
    collection = Collection("inventory")
        
    for object in collection.find(parent = objuuid):
        nodes = __get_child_nodes(nodes, object, collection)
    
    return nodes

def no_fixed_objects(objuuid):
    no_objects_found = True
    for node in get_child_nodes(objuuid):
        if node["id"] in FIXED_OBJUUIDS:
            no_objects_found = False
    return no_objects_found

def __get_fq_name(name, object, collection):
    if "parent" in object:
        if object["parent"] is not "#":
            return __get_fq_name(name, collection.get_object(object["parent"]).object, collection) + "/" + object["name"]
        else:
            return name + "/" + object["name"]
    else:
        return name + "/" + object["name"]
    
def get_fq_name(objuuid):
    collection = Collection("inventory")
    
    return __get_fq_name("", collection.get_object(objuuid).object, collection)
    
def set_parent_objuuid(objuuid, parent_objuuid):
    assert objuuid not in FIXED_OBJUUIDS, f"Change parent not permitted for {objuuid}"
    assert parent_objuuid not in FIXED_OBJUUIDS, f"Change parent not permitted for {parent_objuuid}"
    
    if objuuid != parent_objuuid:
        collection = Collection("inventory")
    
        current = collection.get_object(objuuid)
        assert current.object["type"] is "user", f"Change parent not permitted for {objuuid}"
        
        old_parent_objuuid = current.object["parent"]
        current.object["parent"] = parent_objuuid
        current.set()
        
        if old_parent_objuuid != '#':
            parent = collection.get_object(old_parent_objuuid)
            parent.object["children"] = collection.find_objuuids(parent = old_parent_objuuid)
            parent.set()
        
        if parent_objuuid != '#':
            new_parent = collection.get_object(parent_objuuid)
            new_parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
            new_parent.set()
    
def delete_node(objuuid):
    assert objuuid not in FIXED_OBJUUIDS, f"Deletion is not permitted for {objuuid}"
    assert no_fixed_objects(objuuid), f"Deletion is not permitted because {objuuid} contains fixed objects"

    collection = Collection("inventory")
    
    parent_objuuid = collection.get_object(objuuid).object["parent"]
    
    for node in get_child_nodes(objuuid):
        current = collection.get_object(node["id"])
        
        if "type" in current.object and \
           "sequuid" in current.object:
            if current.object["type"] == "binary file":
                delete_sequence(current.object["sequuid"])
                
        current.destroy()
    
    current = collection.get_object(objuuid)
    
    if "type" in current.object and \
       "sequuid" in current.object:
        if current.object["type"] == "binary file":
            delete_sequence(current.object["sequuid"])
    
    current.destroy()
    
    if parent_objuuid != "#":
        parent = collection.get_object(parent_objuuid)
        parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
        parent.set()
    
def get_context_menu(objuuid):
    return Collection("inventory").get_object(objuuid).object["context"]

def recstrrepl(object, find, replace):
    if isinstance(object, dict):
        for key, value in object.items():
            if isinstance(value, dict) or isinstance(value, list):
                recstrrepl(object[key], find, replace)
            else:
                try:
                    object[key] = object[key].replace(find, replace)
                except:
                    pass
    elif isinstance(object, list):
        for i, value in enumerate(object):
            if isinstance(value, dict) or isinstance(value, list):
                recstrrepl(object[i], find, replace)
            else:
                try:
                    object[i] = object[i].replace(find, replace)
                except:
                    pass
    else:
        try:
            object = object.replace(find, replace)
        except:
            pass

def __copy_object(objuuid, parent_objuuid, collection, old_objuuids, new_objuuids):
    current = collection.get_object(objuuid)
    
    if "parent" in current.object and \
       "type" in current.object and \
       "name" in current.object:
        child_objuuids = collection.find_objuuids(parent = objuuid)
        
        clone = collection.get_object()
        
        clone.object = current.object
        clone.object["children"] = []
        clone.object["parent"] = parent_objuuid
        
        add_message("copied " + clone.object["name"])
        
        recstrrepl(clone.object, objuuid, clone.objuuid)

        if clone.object["type"] == "binary file":
            clone.object["sequuid"] = copy_sequence(clone.object["sequuid"])
            
        clone.set()
        
        parent = collection.get_object(clone.object["parent"])
        parent.object["children"] = collection.find_objuuids(parent = clone.object["parent"])
        parent.set()
        
        old_objuuids.append(objuuid)
        new_objuuids.append(clone.objuuid)
        
        for child_objuuid in child_objuuids:
            __copy_object(child_objuuid, clone.objuuid, collection, old_objuuids, new_objuuids)
    else:
        current.destroy()

def copy_object(objuuid):
    assert objuuid not in FIXED_OBJUUIDS, f"Copying is not permitted for {objuuid}"
    assert no_fixed_objects(objuuid), f"Copying is not permitted because {objuuid} contains fixed objects"

    collection = Collection("inventory")
    
    current = collection.get_object(objuuid)
    
    child_objuuids = collection.find_objuuids(parent = objuuid)
    
    clone = collection.get_object()
    
    clone.object = current.object
    clone.object["children"] = []
    clone.object["name"] = clone.object["name"] + " (Copy)"
    
    add_message("copied " + clone.object["name"])
    
    recstrrepl(clone.object, objuuid, clone.objuuid)
    
    if clone.object["type"] == "binary file":
        clone.object["sequuid"] = copy_sequence(clone.object["sequuid"])

    clone.set()

    parent = collection.get_object(clone.object["parent"])
    parent.object["children"] = collection.find_objuuids(parent = clone.object["parent"])
    parent.set()
    
    old_objuuids = [objuuid]
    new_objuuids = [clone.objuuid]
    
    for child_objuuid in child_objuuids:
        __copy_object(child_objuuid, clone.objuuid, collection, old_objuuids, new_objuuids)
    
    for n in new_objuuids:
        new = collection.get_object(n)
        
        for i, new_objuuid in enumerate(new_objuuids):
            old_objuuid = old_objuuids[i]
            
            recstrrepl(new.object, old_objuuid, new_objuuid)
            
        new.set()
        
        if "name" in new.object:
            add_message("mutated " + new.object["name"])
        else:
            add_message("mutated " + new.objuuid)

    if len(child_objuuids) > 0:
        touch_flag("inventoryState")

    return clone
    
def import_objects(objects):
    collection = Collection("inventory")
            
    container = create_container("#", "Imported Objects")
    
    objuuids = collection.list_objuuids()

    obj_ttl = len(objects)
    obj_cnt = 1    
    
    for objuuid, object in objects.items():
        try:
            current = collection.get_object(objuuid)
            
            if "parent" in current.object:
                if current.object["parent"] in objuuids:
                    parent = collection.get_object(current.object["parent"])
                    
                    if "children" in parent.object:
                        parent.object["children"].remove(objuuid)
                        parent.set()
                
            if "children" in current.object:
                old_children = current.object["children"]
                current.object = object
                        
                for child in old_children:
                    if child not in current.object["children"]:
                        current.object["children"].append(child)
            else:
                current.object = object
            
            if "parent" in current.object:
                if current.object["parent"] in objuuids:
                    parent = collection.get_object(current.object["parent"])
                    
                    if "children" in parent.object:
                        if objuuid not in parent.object["children"]:
                            parent.object["children"].append(objuuid)
                            parent.set()
                        
            current.set()
            
            add_message("imported ({3} of {4}): {0}, type: {1}, name: {2}".format(objuuid, object["type"], object["name"], obj_cnt, obj_ttl))
            obj_cnt = obj_cnt + 1
        except:
            add_message(traceback.format_exc())
            
    objuuids = collection.list_objuuids()
    for objuuid in objuuids:
        current = collection.get_object(objuuid)
        if "parent" in current.object:
            if current.object["parent"] not in objuuids and \
               current.object["parent"] != "#":
                current.object["parent"] = container.objuuid
                container.object["children"].append(objuuid)
                current.set()
            elif current.object["parent"] != "#":
                parent = collection.get_object(current.object["parent"])
                if current.objuuid not in parent.object["children"]:
                    parent.object["children"].append(current.objuuid)
                    parent.set()
            
    if len(container.object["children"]) > 0:
        container.set()
    else:
        container.destroy()

collection = Collection("inventory")
collection.create_attribute("parent", "['parent']")
collection.create_attribute("type", "['type']")
collection.create_attribute("name", "['name']")
collection.create_attribute("sessionid", "['sessionid']")
    
if not len(collection.find(parent = "#")):
    create_container("#", "Root")

if not len(collection.find(type = "config")):
    create_config()
    create_console_template()
    create_task_template()
    create_public_key()
    create_private_key()
    create_settings_container()

create_users_container()
if not len(collection.find(type = "user")):
    create_users_container()
    user = create_user(name = "root")
    user.object["password"] = "root"
    user.object["enabled"] = True
    user.set()
