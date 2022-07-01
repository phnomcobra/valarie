#!/usr/bin/python3
"""This module implements functions for manipulating the inventory."""

import traceback
from time import sleep
from typing import Any, Dict, List

from valarie.dao.document import Collection, Object
from valarie.dao.datastore import delete_sequence, copy_sequence
from valarie.controller.container import create_container
from valarie.router.messaging import add_message
from valarie.controller import kvstore as kv
from valarie.controller.config import (
    CONFIG_OBJUUID,
    TASK_PROTO_OBJUUID,
    CONSOLE_PROTO_OBJUUID,
    SETTINGS_CONTAINER_OBJUUID,
    create_config,
    create_console_template,
    create_task_template,
    create_settings_container
)

FIXED_OBJUUIDS = (
    CONFIG_OBJUUID,
    TASK_PROTO_OBJUUID,
    CONSOLE_PROTO_OBJUUID,
    SETTINGS_CONTAINER_OBJUUID,
)

IMMOBILE_TYPES = ["result link"]

def lock():
    """This function blocks execution until the inventory lock key in
    the key value store is set to false. Upon sensing false, set the lock
    key to true and return.
    """
    while kv.get('inventory lock', default=False) is True:
        sleep(1)
    kv.set('inventory lock', True)

def unlock():
    """This function sets the inventory lock key ro false in the key value store."""
    kv.set('inventory lock', False)

def __get_child_tree_nodes(nodes: List[Dict], current: Object, inventory: Collection):
    """This is a recursion function used to accumulate nodes used for jstree. This function
    creates a jstree node using an inventory object's UUID, name, icon (optional), type,
    and parent UUID. If the icon key is missing, jstree uses a default icon.

    Args:
        nodes:
            List of nodes being accumulated.

        current:
            Current inventory object being inspected.

        inventory:
            The inventory collection.
    """
    try:
        node = {
            "id": current.objuuid,
            "parent": current.object["parent"],
            "text": current.object["name"],
            "type": current.object["type"]
        }

        if "icon" in current.object:
            node["icon"] = current.object["icon"]

        nodes.append(node)

        for objuuid in inventory.find_objuuids(parent=current.objuuid):
            nodes = __get_child_tree_nodes(nodes, inventory.get_object(objuuid), inventory)
    except KeyError:
        add_message(traceback.format_exc())
        add_message(str(current.object))

    return nodes

def get_child_tree_nodes(objuuid: str) -> List[Dict]:
    """This is a function used to accumulate nodes used for jstree.

    Args:
        nodes:
            List of nodes being accumulated.

        objuuid:
            The UUID of inventory object to begin recursion from.

    Returns:
        A list of node objects.
    """
    nodes = []
    inventory = Collection("inventory")

    for current in inventory.find(parent=objuuid):
        nodes = __get_child_tree_nodes(nodes, current, inventory)

    return nodes

def no_fixed_objects(objuuid: str) -> bool:
    """This is a function checks an inventory object and its children for
    immobilized UUIDs.

    Args:
        objuuid:
            The UUID of inventory object to begin recursion from.

    Returns:
        True if no fixed objects are detected, else false.
    """
    no_objects_found = True
    for node in get_child_tree_nodes(objuuid):
        if node["id"] in FIXED_OBJUUIDS:
            no_objects_found = False
    return no_objects_found

def __get_fq_name(name: str, current: Object, inventory: Collection) -> str:
    """This is a recursion function used to accumulate a fully qualified name of an
    inventory object. Fully qualified names a '/' delimited.

    Args:
        name:
            Name prior to the next level of accumulation.

        current:
            Current inventory object being inspected.

        inventory:
            The inventory collection.

    Returns:
        Name with the next level of accumulation
    """
    if current["parent"] != "#":
        fq_name = __get_fq_name(name, inventory.get_object(current["parent"]).object, inventory)
        return f'{fq_name}/{current["name"]}'
    return f'{name}/{current["name"]}'

def get_fq_name(objuuid: str) -> str:
    """This function used to compute an inventory object's fully qualified name.
    This function is primarily used for creating zip archives.

    Args:
        objuuid:
            The inventory object we're getting the fully qualified name for.

    Returns:
        A string of the fully qualified name.
    """
    inventory = Collection("inventory")
    return __get_fq_name("", inventory.get_object(objuuid).object, inventory)

def set_parent_objuuid(objuuid: str, parent_objuuid: str):
    """This function used to change and inventory object's parent.
    Objects with UUIDs or with parent UUIDs in the fixed objuuids list may not be moved.
    Objects that have a type in the immobile type list type may not be moved.

    Args:
        objuuid:
            The UUID of the inventory object being moved.

        parent_objuuid:
            The UUID of the parent object in the inventory.
    """
    lock()

    assert objuuid not in FIXED_OBJUUIDS, f"Change parent not permitted for {objuuid}"
    assert parent_objuuid not in FIXED_OBJUUIDS, f"Change parent not permitted for {parent_objuuid}"

    inventory = Collection("inventory")
    current = inventory.get_object(objuuid)

    # pylint: disable=line-too-long
    assert current.object['type'] not in IMMOBILE_TYPES, f'''Change parent for {current.object['type']} not permitted'''

    if objuuid != parent_objuuid:
        old_parent_objuuid = current.object["parent"]
        current.object["parent"] = parent_objuuid
        current.set()

        if old_parent_objuuid != '#':
            parent = inventory.get_object(old_parent_objuuid)
            parent.object["children"] = inventory.find_objuuids(parent=old_parent_objuuid)
            parent.set()

        if parent_objuuid != '#':
            new_parent = inventory.get_object(parent_objuuid)
            new_parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
            new_parent.set()

    unlock()

def delete_node(objuuid: str):
    """This function used to delete an inventory object and any child objects it may have.
    Objects with UUIDs or with parent UUIDs in the fixed objuuids list may not be deleted.
    Binary file objects linked to sequences in the datastore collection are delete a swell.

    Args:
        objuuid:
            The UUID of the inventory object being deleted.
    """
    lock()

    assert objuuid not in FIXED_OBJUUIDS, f"Deletion is not permitted for {objuuid}"
    # pylint: disable=line-too-long
    assert no_fixed_objects(objuuid), f"Deletion is not permitted because {objuuid} contains fixed objects"

    inventory = Collection("inventory")

    parent_objuuid = inventory.get_object(objuuid).object["parent"]

    for node in get_child_tree_nodes(objuuid):
        current = inventory.get_object(node["id"])

        if "type" in current.object and \
           "sequuid" in current.object:
            if current.object["type"] == "binary file":
                delete_sequence(current.object["sequuid"])

        current.destroy()

    current = inventory.get_object(objuuid)

    if "type" in current.object and \
       "sequuid" in current.object:
        if current.object["type"] == "binary file":
            delete_sequence(current.object["sequuid"])

    current.destroy()

    if parent_objuuid != "#":
        parent = inventory.get_object(parent_objuuid)
        parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
        parent.set()

    unlock()

def get_context_menu(objuuid: str) -> List[Dict]:
    """This function used to delete an inventory object and any child objects it may have.
    Objects with UUIDs or with parent UUIDs in the fixed objuuids list may not be deleted.
    Binary file objects linked to sequences in the datastore collection are delete a swell.

    Args:
        objuuid:
            The UUID of the inventory object.

    Returns:
        Returns a list of dictionaries from inventory object's context key.
    """
    return Collection("inventory").get_object(objuuid).object["context"]

def recstrrepl(current: Any, find: str, replace: str):
    """This is a function used to replace a string in a list or dictionary.
    The replacement is attempted against all keys.

    Args:
        object:
            The list or dictionary being acted upon.

        find:
            The string be searched for.

        replace:
            The string to replace the search string with.
    """
    if isinstance(current, dict):
        for key, value in current.items():
            if isinstance(value, (dict, list)):
                recstrrepl(current[key], find, replace)
            elif isinstance(current[key], str):
                current[key] = current[key].replace(find, replace)
    elif isinstance(current, list):
        for i, value in enumerate(current):
            if isinstance(value, (dict, list)):
                recstrrepl(current[i], find, replace)
            elif isinstance(current[i], str):
                current[i] = current[i].replace(find, replace)
    elif isinstance(current, str):
        current = current.replace(find, replace)

def __copy_object(
        objuuid: str,
        parent_objuuid: str,
        inventory: Collection,
        old_objuuids: List[str],
        new_objuuids: List[str]
    ):
    """This is a recursion function used to copy and object in the inventory and
    any of the children it may have. Copied objects will have new UUIDs. As this
    function runs, a mapping is accumulated between the original and cloned UUIDs.

    Args:
        objuuid:
            The UUID of the inventory object being copied.

        parent_objuuid:
            The UUID of the inventory object's parent.

        inventory:
            The inventory collection.

        old_objuuids:
            List of object UUIDs that copied.

        new_objuuids:
            List of object UUIDs that were precipitated from the copy.
    """
    current = inventory.get_object(objuuid)

    if (
            "parent" in current.object and
            "type" in current.object and
            "name" in current.object
        ):
        child_objuuids = inventory.find_objuuids(parent=objuuid)

        clone = inventory.get_object()

        clone.object = current.object
        clone.object["children"] = []
        clone.object["parent"] = parent_objuuid

        add_message(f'copied {clone.object["name"]}')

        recstrrepl(clone.object, objuuid, clone.objuuid)

        if clone.object["type"] == "binary file":
            clone.object["sequuid"] = copy_sequence(clone.object["sequuid"])

        clone.set()

        parent = inventory.get_object(clone.object["parent"])
        parent.object["children"] = inventory.find_objuuids(parent=clone.object["parent"])
        parent.set()

        old_objuuids.append(objuuid)
        new_objuuids.append(clone.objuuid)

        for child_objuuid in child_objuuids:
            __copy_object(child_objuuid, clone.objuuid, inventory, old_objuuids, new_objuuids)
    else:
        current.destroy()

def copy_object(objuuid: str) -> Object:
    """This function copies an object in the inventory and any of the child objects it may have.
    Copied objects will have new UUIDs. References in copied procedures, controllers, tasks,
    and text files are remapped to the new UUIDs of the copied inventory objects.
    Objects with UUIDs or with parent UUIDs in the fixed objuuids list may not be moved.

    Args:
        objuuid:
            The UUID of the inventory object being copied.

    Returns:
        The copied inventory object.
    """
    lock()

    assert objuuid not in FIXED_OBJUUIDS, f"Copying is not permitted for {objuuid}"
    # pylint: disable=line-too-long
    assert no_fixed_objects(objuuid), f"Copying is not permitted because {objuuid} contains fixed objects"

    inventory = Collection("inventory")

    current = inventory.get_object(objuuid)

    child_objuuids = inventory.find_objuuids(parent=objuuid)

    clone = inventory.get_object()

    clone.object = current.object
    clone.object["children"] = []
    clone.object["name"] = clone.object["name"] + " (Copy)"

    add_message(f'copied {clone.object["name"]}')

    recstrrepl(clone.object, objuuid, clone.objuuid)

    if clone.object["type"] == "binary file":
        clone.object["sequuid"] = copy_sequence(clone.object["sequuid"])

    clone.set()

    parent = inventory.get_object(clone.object["parent"])
    parent.object["children"] = inventory.find_objuuids(parent=clone.object["parent"])
    parent.set()

    old_objuuids = [objuuid]
    new_objuuids = [clone.objuuid]

    for child_objuuid in child_objuuids:
        __copy_object(child_objuuid, clone.objuuid, inventory, old_objuuids, new_objuuids)

    for uuid in new_objuuids:
        new = inventory.get_object(uuid)

        for i, new_objuuid in enumerate(new_objuuids):
            old_objuuid = old_objuuids[i]

            recstrrepl(new.object, old_objuuid, new_objuuid)

        new.set()

        if "name" in new.object:
            add_message(f'mutated {new.object["name"]}')
        else:
            add_message(f'mutated {new.objuuid}')

    if len(child_objuuids) > 0:
        kv.touch("inventoryState")

    unlock()

    return clone

# pylint: disable=too-many-branches
def import_objects(objects: Dict[str, Object]):
    """This function imports objects into the inventory.

    Args:
        objects:
            Dictionary of collection objects to import.
    """
    inventory = Collection("inventory")

    container = create_container("#", "Imported Objects")

    objuuids = inventory.list_objuuids()

    obj_ttl = len(objects)
    obj_cnt = 1

    # pylint: disable=too-many-nested-blocks
    for objuuid, imported_object in objects.items():
        try:
            current = inventory.get_object(objuuid)

            if "parent" in current.object:
                if current.object["parent"] in objuuids:
                    parent = inventory.get_object(current.object["parent"])

                    if "children" in parent.object:
                        parent.object["children"].remove(objuuid)
                        parent.set()

            if "children" in current.object:
                old_children = current.object["children"]
                current.object = imported_object

                for child in old_children:
                    if child not in current.object["children"]:
                        current.object["children"].append(child)
            else:
                current.object = imported_object

            if "parent" in current.object:
                if current.object["parent"] in objuuids:
                    parent = inventory.get_object(current.object["parent"])

                    if "children" in parent.object:
                        if objuuid not in parent.object["children"]:
                            parent.object["children"].append(objuuid)
                            parent.set()

            current.set()

            add_message(f'imported ({obj_cnt} of {obj_ttl}): {objuuid},'\
                        f'type: {imported_object["type"]}, name: {imported_object["name"]}')
            obj_cnt += 1
        except: # pylint: disable=bare-except
            add_message(traceback.format_exc())

    objuuids = inventory.list_objuuids()
    for objuuid in objuuids:
        current = inventory.get_object(objuuid)
        if "parent" in current.object:
            if current.object["parent"] not in objuuids and \
               current.object["parent"] != "#":
                current.object["parent"] = container.objuuid
                container.object["children"].append(objuuid)
                current.set()
            elif current.object["parent"] != "#":
                parent = inventory.get_object(current.object["parent"])
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

if not collection.find(parent="#"):
    create_container("#", "Root")

if not collection.find(type="config"):
    create_config()
    create_console_template()
    create_task_template()
    create_settings_container()

unlock()
