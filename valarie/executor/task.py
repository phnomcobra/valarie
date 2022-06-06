#!/usr/bin/python3

import traceback

from valarie.dao.document import Collection
from valarie.dao.ramdocument import Collection as RAMCollection
from valarie.controller.messaging import add_message

from imp import new_module
from time import time

class TaskError:
    def __init__(self, uuid):
        self.output = ['<font color="red">'] + traceback.format_exc().split("\n") + ["</font>"]
        self.uuid = uuid
        self.status = 5 

    def execute(self, cli):
        return self.status

def execute(tskuuid, hstuuid):
    inventory = Collection("inventory")
    results = RAMCollection("results")
    
    for result in results.find(hstuuid = hstuuid, tskuuid = tskuuid):
        result.destroy()
    
    result = results.get_object()
    
    result.object['start'] = time()
        
    status_code_body = ""
    status_data = {}
    
    for status in inventory.find(type = "status"):
        try:
            status_code_body += "{0}=int('{1}')\n".format(status.object["alias"], status.object["code"])
            status_data[int(status.object["code"])] = status.object
        except:
            add_message(traceback.format_exc())
    
    host = inventory.get_object(hstuuid)
    result.object['host'] = {}
    result.object['host']['host'] = host.object['host']
    result.object['host']['name'] = host.object['name']
    result.object['host']['objuuid'] = hstuuid
    
    tempmodule = new_module("tempmodule")
    
    try:
        exec(inventory.get_object(host.object["console"]).object["body"], tempmodule.__dict__)
        cli = tempmodule.Console(host = host.object)
        
        try:
            inv_task = inventory.get_object(tskuuid)
            
            result.object['task'] = {}
            result.object['task']["name"] = inv_task.object["name"]
            result.object['task']["start"] = None
            result.object['task']["stop"] = None
            result.object['task']["tskuuid"] = tskuuid
            
            inv_task.object["body"] in tempmodule.__dict__
            exec(inv_task.object["body"] + "\n" + status_code_body, tempmodule.__dict__)
            task = tempmodule.Task()
            
            try:
                task.execute(cli)
            except:
                task = TaskError(tskuuid)
                add_message(traceback.format_exc())
        except:
            task = TaskError(tskuuid)
            add_message(traceback.format_exc())
    except:
        task = TaskError(tskuuid)
        add_message(traceback.format_exc())
        
    result.object['output'] = task.output
    
    try:
        result.object['status'] = status_data[task.status]
        
        result.object['status'] = {}
        result.object['status']["name"] = status_data[task.status]["name"]
        result.object['status']["code"] = status_data[task.status]["code"]
        result.object['status']["abbreviation"] = status_data[task.status]["abbreviation"]
        result.object['status']["cfg"] = status_data[task.status]["cfg"]
        result.object['status']["cbg"] = status_data[task.status]["cbg"]
        result.object['status']["sfg"] = status_data[task.status]["sfg"]
        result.object['status']["sbg"] = status_data[task.status]["sbg"]
    except:
        add_message(traceback.format_exc())
        result.object['status'] = {"code" : task.status}
        
    result.object['stop'] = time()
    result.set()
    
    return result.object
