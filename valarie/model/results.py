#!/usr/bin/python3

from threading import Timer
from time import time

from valarie.executor.timers import timers
from valarie.dao.document import Collection
from valarie.model.inventory import delete_node
from valarie.controller.flags import touch_flag

def create_result_link(parent_objuuid, name="New Result Link", objuuid=None):
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

def delete(objuuid):
    results = Collection("results")
    results.get_object(objuuid).destroy()

def get_hosts(hstuuid, hstuuids, grpuuids, inventory):
    o = inventory.get_object(hstuuid)
    
    if "type" in o.object:
        if o.object["type"] == "host":
            if hstuuid not in hstuuids:
                hstuuids.append(hstuuid)
        elif o.object["type"] == "host group":
            for uuid in o.object["hosts"]:
                c = inventory.get_object(uuid)
                if "type" in c.object:
                    if c.object["type"] == "host group":
                        if uuid not in grpuuids:
                            grpuuids.append(uuid)
                            get_hosts(uuid, hstuuids, grpuuids, inventory)
                    elif c.object["type"] == "host":
                        if uuid not in hstuuids:
                            hstuuids.append(uuid)
                else:
                    o.object["hosts"].remove(uuid)
                    o.set()
                    c.destroy()
    
def get_controller_results(ctruuid):
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
                for r in results.find(hstuuid=hstuuid, prcuuid=prcuuid):
                    if result is None:
                        result = r.object
                    elif result['start'] < r.object['start']:
                        result = r.object
                
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

def get_procedure_result(prcuuid, hstuuid):
    inventory = Collection("inventory")
    results = Collection("results")
    
    result_objects = []
            
    hstuuids = []
    grpuuids = []
    get_hosts(hstuuid, hstuuids, grpuuids, inventory)

    for hstuuid in hstuuids:
        try:
            result = None
            for r in results.find(hstuuid=hstuuid, prcuuid=prcuuid):
                if result is None:
                    result = r.object
                elif result['start'] < r.object['start']:
                    result = r.object
            
            if result["start"] != None and result["stop"] != None:
                result["duration"] = result["stop"] - result["start"]
            elif result["start"] != None:
                result["duration"] = time() - result["start"]
            else:
                result["duration"] = 0
            
            result_objects.append(result)
        except IndexError:
            continue
    
    return result_objects

def get_result(resuuid):
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

            if time() - result.object["start"] > expiration_period and expiration_period is not 0:
                if "linkuuid" in result.object:
                    delete_node(result.object['linkuuid'])
                    if update_inventory:
                        refresh_inventory = True

                result.destroy()
        except:
            result.destroy()
    
    if refresh_inventory:
        touch_flag("inventoryState")
    
collection = Collection("results")
collection.create_attribute("start", "['start']")
collection.create_attribute("stop", "['stop']")
collection.create_attribute("tskuuid", "['task']['objuuid']")
collection.create_attribute("prcuuid", "['procedure']['objuuid']")
collection.create_attribute("hstuuid", "['host']['objuuid']")

timers["results worker"] = Timer(60, worker)
timers["results worker"].start()
