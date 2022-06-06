#!/usr/bin/python3

from threading import Timer
from time import time

from valarie.executor.timers import timers
from valarie.dao.ramdocument import Collection as RAMCollection
from valarie.dao.document import Collection

def delete(objuuid):
    collection = RAMCollection("results")
    collection.get_object(objuuid).destroy()

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
    results = RAMCollection("results")
    
    collection = Collection("inventory")
    
    controller = collection.get_object(ctruuid)
    
    controller_results = []
    
    hstuuids = []
    grpuuids = []
    for hstuuid in controller.object["hosts"]:
        get_hosts(hstuuid, hstuuids, grpuuids, collection)
    
    for hstuuid in hstuuids:
        for prcuuid in controller.object["procedures"]:
            try:
                result = results.find(hstuuid = hstuuid, prcuuid = prcuuid)[0].object
                
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
            except IndexError:
                continue
    
    return controller_results

def get_procedure_result(prcuuid, hstuuid):
    collection = Collection("inventory")
    
    results = RAMCollection("results")
    
    result_objects = []
            
    hstuuids = []
    grpuuids = []
    get_hosts(hstuuid, hstuuids, grpuuids, collection)

    for hstuuid in hstuuids:
        try:
            result = results.find(hstuuid = hstuuid, prcuuid = prcuuid)[0].object
            
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
    

def worker():
    timers["results worker"] = Timer(60, worker)
    timers["results worker"].start()
    
    results = RAMCollection("results")
    
    for objuuid in results.list_objuuids():
        result = results.get_object(objuuid)
        
        try:
            if time() - result.object["start"] > 86400:
                result.destroy()
        except:
            result.destroy()
    
collection = RAMCollection("results")
collection.create_attribute("start", "['start']")
collection.create_attribute("stop", "['stop']")
collection.create_attribute("tskuuid", "['task']['objuuid']")
collection.create_attribute("prcuuid", "['procedure']['objuuid']")
collection.create_attribute("hstuuid", "['host']['objuuid']")

timers["results worker"] = Timer(60, worker)
timers["results worker"].start()
