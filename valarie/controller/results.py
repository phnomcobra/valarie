#!/usr/bin/python3
"""This module implements functions for result link objects; retrieving
results by controller, procedure, and result UUID; deleting results; and
the results worker."""
from threading import Timer
from time import time
from typing import Dict, List

from valarie.executor.timers import timers
from valarie.dao.document import Collection, Object
from valarie.controller.inventory import delete_node
from valarie.controller import kvstore as kv

def create_result_link(
        parent_objuuid: str,
        name: str = "New Result Link",
        objuuid: str = None
    ) -> Object:
    """This is a function used to create a result link object in the inventory.

    Args:
        parent_objuuid:
            Parent object UUID.

        name:
            Name of the link object.

        objuuid:
            UUID of the link object.

    Returns:
        An inventory object.
    """
    inventory = Collection("inventory")

    result = inventory.get_object(objuuid)

    result.object = {
        "type" : "result link",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "icon" : "/images/result_icon.png",
        "context" : {
            "open" : {
                "label" : "Open",
                "action" : {
                    "method" : "open result",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : result.objuuid
                    }
                }
            }
        }
    }

    result.set()

    if parent_objuuid != "#":
        parent = inventory.get_object(parent_objuuid)
        parent.object["children"] = inventory.find_objuuids(parent=parent_objuuid)
        parent.set()

    return result

def get_hosts(
        hstuuid: str,
        hstuuids: List[str],
        grpuuids: List[str],
        inventory: Collection
    ):
    """This is a recursion function used to aggregate all of the nested hosts that a
    host, more precisely a host group encapsulates.

    Args:
        hstuuid:
            The host or host group object that recusion begins from.

        hstuuids:
            List of accumulated host object UUIDs.

        grpuuids:
            List of accumulated host group object UUIDs.

        inventory:
            The inventory collection.
    """
    current = inventory.get_object(hstuuid)

    if "type" in current.object:
        if current.object["type"] == "host":
            if hstuuid not in hstuuids:
                hstuuids.append(hstuuid)
        elif current.object["type"] == "host group":
            for uuid in current.object["hosts"]:
                nested = inventory.get_object(uuid)
                if "type" in nested.object:
                    if nested.object["type"] == "host group":
                        if uuid not in grpuuids:
                            grpuuids.append(uuid)
                            get_hosts(uuid, hstuuids, grpuuids, inventory)
                    elif nested.object["type"] == "host":
                        if uuid not in hstuuids:
                            hstuuids.append(uuid)
                else:
                    current.object["hosts"].remove(uuid)
                    current.set()
                    nested.destroy()

def get_controller_results(ctruuid: str) -> List[Dict]:
    """This is a function used to retrieve the latest results for a
    controller object.

    Args:
        ctruuid:
            The controller object UUID.

    Returns:
        List of result dictionaries.
    """
    results = Collection("results")
    inventory = Collection("inventory")

    controller = inventory.get_object(ctruuid)

    controller_results = []

    hstuuids = []
    grpuuids = []
    for hstuuid in controller.object["hosts"]:
        get_hosts(hstuuid, hstuuids, grpuuids, inventory)

    for hstuuid in hstuuids:
        for prcuuid in controller.object["procedures"]:
            try:
                result = None
                for current in results.find(hstuuid=hstuuid, prcuuid=prcuuid):
                    if result is None:
                        result = current.object
                    elif result['start'] < current.object['start']:
                        result = current.object

                if result["start"] != None and result["stop"] != None:
                    result["duration"] = result["stop"] - result["start"]
                elif result["start"] != None:
                    result["duration"] = time() - result["start"]
                else:
                    result["duration"] = 0

                if result["stop"] == None:
                    result["age"] = 0
                else:
                    result["age"] = time() - result["stop"]

                controller_results.append(result)
            except:
                continue

    return controller_results

def get_procedure_result(prcuuid: str, hstuuid: str) -> List[Dict]:
    """This is a function used to retrieve the latest results for a
    particular host/procedure combination.

    Args:
        prcuuid:
            The procedure object UUID.

        hstuuid:
            The host object UUID.

    Returns:
        List of result dictionaries.
    """
    inventory = Collection("inventory")
    results = Collection("results")

    result_objects = []

    hstuuids = []
    grpuuids = []
    get_hosts(hstuuid, hstuuids, grpuuids, inventory)

    for hstuuid in hstuuids:
        try:
            result = None
            # get the latest result for a host/procedure UUID pair.
            for current in results.find(hstuuid=hstuuid, prcuuid=prcuuid):
                if result is None:
                    result = current.object
                elif result['start'] < current.object['start']:
                    result = current.object

            if result["start"] != None and result["stop"] != None:
                result["duration"] = result["stop"] - result["start"]
            elif result["start"] != None:
                result["duration"] = time() - result["start"]
            else:
                result["duration"] = 0

            result_objects.append(result)
        except:
            continue

    return result_objects

def get_result(resuuid: str) -> List[Dict]:
    """This is a function used to retrieve a specific result.

    Args:
        resuuid:
            The result object UUID.

    Returns:
        List of result dictionaries.
    """
    results = Collection("results")
    result = results.get_object(resuuid)

    if result.object["start"] != None and result.object["stop"] != None:
        result.object["duration"] = result.object["stop"] - result.object["start"]
    elif result.object["start"] != None:
        result.object["duration"] = time() - result.object["start"]
    else:
        result.object["duration"] = 0

    return [result.object]

def worker():
    """This is a worker function used to process expiration of results
    and result links."""
    timers["results worker"] = Timer(60, worker)
    timers["results worker"].start()

    results = Collection("results")
    inventory = Collection('inventory')
    refresh_inventory = False

    for objuuid in results.list_objuuids():
        result = results.get_object(objuuid)
        try:
            procedure = inventory.get_object(result.object['procedure']['objuuid'])

            try:
                expiration_period = int(procedure.object['resultexpirationperiod'])
            except:
                expiration_period = 3600

            try:
                update_inventory = ('true' in str(procedure.object['resultinventoryupdate']).lower())
            except:
                update_inventory = False

            if time() - result.object["start"] > expiration_period and expiration_period != 0:
                if "linkuuid" in result.object:
                    delete_node(result.object['linkuuid'])
                    if update_inventory:
                        refresh_inventory = True

                result.destroy()
        except:
            result.destroy()

    if refresh_inventory:
        kv.touch("inventoryState")

collection = Collection("results")
collection.create_attribute("start", "['start']")
collection.create_attribute("stop", "['stop']")
collection.create_attribute("tskuuid", "['task']['objuuid']")
collection.create_attribute("prcuuid", "['procedure']['objuuid']")
collection.create_attribute("hstuuid", "['host']['objuuid']")

timers["results worker"] = Timer(60, worker)
timers["results worker"].start()
