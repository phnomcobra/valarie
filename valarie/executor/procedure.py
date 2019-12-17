#!/usr/bin/python

MAX_JOBS = 20

import traceback
import json

from threading import Lock, Thread, Timer
from time import time
from datetime import datetime
from imp import new_module

from valarie.dao.document import Collection
from valarie.dao.ramdocument import Collection as RAMCollection
from valarie.dao.utils import sucky_uuid
from valarie.controller.flags import touch_flag
from valarie.controller.messaging import add_message

jobs = {}
job_lock = Lock()

def update_job(jobuuid, key, value):
    job_lock.acquire()
    jobs[jobuuid][key] = value
    job_lock.release()
    touch_flag("queueState")
    
def set_job(jobuuid, value):
    job_lock.acquire()
    jobs[jobuuid] = value
    job_lock.release()
    touch_flag("queueState")
    
def get_job(jobuuid):
    try:
        job_lock.acquire()
        jobs[jobuuid]
    except KeyError:
        jobs[jobuuid] = None
    finally:
        job_lock.release()
        return jobs[jobuuid]

def del_job(jobuuid):
    try:
        job_lock.acquire()
        del jobs[jobuuid]
    except KeyError:
        pass
    finally:
        touch_flag("queueState")
        job_lock.release()

def get_jobs_grid():
    grid_data = []
    job_lock.acquire()
    
    for jobuuid, dict in jobs.items():
        row = {}
        row["name"] = dict["procedure"]["name"]
        row["host"] = dict["host"]["name"]
        row["progress"] = dict["progress"]
        grid_data.append(row)
    
    job_lock.release()
    
    for i in range(0, len(grid_data)):
        for j in range(i, len(grid_data)):
            if grid_data[i]["progress"] < grid_data[j]["progress"]:
                grid_data[i], grid_data[j] = grid_data[j], grid_data[i]
    
    return grid_data

def get_queued_hosts(prcuuid):
    hstuuids = []
    
    job_lock.acquire()
    
    for jobuuid, dict in jobs.items():
        if prcuuid == dict["procedure"]["objuuid"]:
            hstuuids.append(dict["host"]["objuuid"])

    job_lock.release()

    return hstuuids


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
    
def queue_procedure(hstuuid, prcuuid, session, ctruuid = None):
    inventory = Collection("inventory")
    
    # Discover Nested Hosts
    discovered_hstuuids = []
    grpuuids = []
    get_hosts(hstuuid, discovered_hstuuids, grpuuids, inventory)
    
    # Exclude Hosts Already Queued
    queued_hstuuids = get_queued_hosts(prcuuid)
    hstuuids = []
    for hstuuid in discovered_hstuuids:
        if hstuuid not in queued_hstuuids:
            hstuuids.append(hstuuid)
    
    temp = inventory.get_object(prcuuid)
    
    if "type" in temp.object:
        if temp.object["type"] == "procedure":
            for hstuuid in hstuuids:
                add_message("Queued host: {0}, procedure {1}...".format(hstuuid, prcuuid))

                host = inventory.get_object(hstuuid)
                
                if host.object["type"] == "host":
                    jobuuid = sucky_uuid()

                    console = inventory.get_object(host.object["console"])
                    
                    job = {
                        "jobuuid" : jobuuid,
                        "host" : host.object,
                        "console" : console.object,
                        "procedure" : temp.object,
                        "session" : session,
                        "process" : None,
                        "queue time" : time(),
                        "start time" : None,
                        "progress" : 0,
                        "ctruuid" : ctruuid
                    }
                
                    set_job(jobuuid, job)
        elif temp.object["type"] == "task":
            for hstuuid in hstuuids:
                add_message("Queued host: {0}, task {1}...".format(hstuuid, prcuuid))
                
                host = inventory.get_object(hstuuid)
                if host.object["type"] == "host":
                    jobuuid = sucky_uuid()

                    console = inventory.get_object(host.object["console"])
                
                    job = {
                        "jobuuid" : jobuuid,
                        "host" : host.object,
                        "console" : console.object,
                        "procedure" : {
                            "objuuid" : prcuuid,
                            "type" : "procedure",
                            "name" : temp.object["name"],
                            "tasks" : [prcuuid],
                            "hosts" : [],
                            "title" : "",
                            "description" : "This is a synthetic procedure used for encapsulating tasks for use with controller objects."
                        },
                        "session" : session,
                        "process" : None,
                        "queue time" : time(),
                        "start time" : None,
                        "progress" : 0,
                        "ctruuid" : ctruuid
                    }
                    
                    set_job(jobuuid, job)
    else:
        temp.destroy()
    
class TaskError:
    def __init__(self, uuid):
        self.output = ['<font color="red">'] + traceback.format_exc().split("\n") + ["</font>"]
        self.uuid = uuid
        self.status = 5 

    def execute(self, cli):
        return self.status

def run_procedure(host_object, procedure_object, console_object, session, jobuuid = None, ctruuid = None):
    add_message("Executing host: {0}, procedure: {1}...".format(host_object["name"], procedure_object["name"]))
    
    inventory = Collection("inventory")
    results = RAMCollection("results")
    
    for result in results.find(hstuuid = host_object["objuuid"], prcuuid = procedure_object["objuuid"]):
        result.destroy()
    
    result = results.get_object()
    
    result.object['start'] = time()
    result.object["output"] = []
    
    status_code_body = ""
    status_data = {}
    
    result.object["output"].append("importing status codes...")
    
    for status in inventory.find(type = "status"):
        try:
            status_code_body += "{0}=int('{1}')\n".format(status.object["alias"], status.object["code"])
            status_data[int(status.object["code"])] = status.object
        except:
            result.object["output"] += traceback.format_exc().split("\n")
    
    result.object['host'] = {}
    result.object['host']['host'] = host_object['host']
    result.object['host']['name'] = host_object['name']
    result.object['host']['objuuid'] = host_object['objuuid']
    
    tempmodule = new_module("tempmodule")
    
    winning_status = None
    continue_procedure = True
    
    result.object["tasks"] = []
    
    result.object['procedure'] = {}
    result.object['procedure']['name'] = procedure_object['name']
    result.object['procedure']['title'] = procedure_object['title']
    result.object['procedure']['description'] = procedure_object['description']
    result.object['procedure']['objuuid'] = procedure_object['objuuid']
    
    try:
        tskuuids = procedure_object["tasks"]
    except:
        add_message(traceback.format_exc())
        
    try:
        for seq_num, tskuuid in enumerate(tskuuids):
            task_result = {}
            task_result["name"] = inventory.get_object(tskuuid).object["name"]
            task_result["start"] = None
            task_result["stop"] = None
            task_result["tskuuid"] = tskuuid
            
            try:
                exec(inventory.get_object(tskuuid).object["body"] + "\n" + status_code_body, tempmodule.__dict__)
                task = tempmodule.Task()
            except:
                task = TaskError(tskuuid)
            
            task_result["output"] = task.output
            try:
                task_result["status"] = {}
                task_result["status"]["name"] = status_data[task.status]["name"]
                task_result["status"]["code"] = status_data[task.status]["code"]
                task_result["status"]["abbreviation"] = status_data[task.status]["abbreviation"]
                task_result["status"]["cfg"] = status_data[task.status]["cfg"]
                task_result["status"]["cbg"] = status_data[task.status]["cbg"]
                task_result["status"]["sfg"] = status_data[task.status]["sfg"]
                task_result["status"]["sbg"] = status_data[task.status]["sbg"]
            except:
                task_result['status'] = {"code" : task.status}
            
            result.object['tasks'].append(task_result)
        
        result.object['status'] = {
            "name" : "Executing",
            "code" : 0,
            "abbreviation" : "EXEC",
            "cfg" : "000000",
            "cbg" : "FFFFFF",
            "sfg" : "000000",
            "sbg" : "999999"
        }
        
        result.object['stop'] = None
        result.set()

        if host_object["objuuid"] in procedure_object["hosts"]:
            touch_flag("procedure-" + procedure_object["objuuid"])
        if ctruuid:
            touch_flag("controller-" + ctruuid)
    except:
        add_message(traceback.format_exc())
    
    procedure_status = None
    
    try:
        try:
            result.object["output"].append("importing console...")
            exec(console_object["body"], tempmodule.__dict__)
            cli = tempmodule.Console(session = session, host = host_object)
        except:
            result.object["output"] += traceback.format_exc().split("\n")
        
        for seq_num, tskuuid in enumerate(tskuuids):
            task_result = {}
            task_result["name"] = inventory.get_object(tskuuid).object["name"]
            task_result["start"] = None
            task_result["stop"] = None
            
            try:
                exec(inventory.get_object(tskuuid).object["body"] + "\n" + status_code_body, tempmodule.__dict__)
                task = tempmodule.Task()
                
                if continue_procedure:
                    task_result["start"] = time()
                    
                    try:
                        task.execute(cli)
                    except:
                        task = TaskError(tskuuid)
                    
                    task_result["stop"] = time()
            except:
                task = TaskError(tskuuid)
                result.object["output"] += traceback.format_exc().split("\n")
            
            task_result["output"] = task.output
            try:
                task_result["output"] = task.output
            
                task_result["status"] = {}
                task_result["status"]["name"] = status_data[task.status]["name"]
                task_result["status"]["code"] = status_data[task.status]["code"]
                task_result["status"]["abbreviation"] = status_data[task.status]["abbreviation"]
                task_result["status"]["cfg"] = status_data[task.status]["cfg"]
                task_result["status"]["cbg"] = status_data[task.status]["cbg"]
                task_result["status"]["sfg"] = status_data[task.status]["sfg"]
                task_result["status"]["sbg"] = status_data[task.status]["sbg"]
            
                try:
                    continue_flag = procedure_object["continue {0}".format(task.status)]
                    
                    if continue_flag == 'false':
                        continue_flag = False
                    
                    if not continue_flag:
                        continue_procedure = False
                except:
                    continue_procedure = False
            except:
                task_result['status'] = {"code" : task.status}
                continue_procedure = False
                
            result.object['tasks'][seq_num] = task_result
            
            if winning_status == None:
                winning_status = task.status
                procedure_status = task_result['status']
            elif task.status < winning_status:
                winning_status = task.status
                procedure_status = task_result['status']
            
            if jobuuid:
                update_job(jobuuid, "progress", float(seq_num + 1) / float(len(tskuuids)))
            
            result.object['stop'] = time()
            result.set()

            if host_object["objuuid"] in procedure_object["hosts"]:
                touch_flag("procedure-" + procedure_object["objuuid"])
            if ctruuid:
                touch_flag("controller-" + ctruuid)
        
        if procedure_status != None:
            result.object['status'] = procedure_status
            result.set()
            
            if host_object["objuuid"] in procedure_object["hosts"]:
                touch_flag("procedure-" + procedure_object["objuuid"])
            if ctruuid:
                touch_flag("controller-" + ctruuid)
    except:
        add_message(traceback.format_exc())
    
    return result.object

def eval_cron_field(cron_str, now_val):
    result = False
    
    try:
        for field in cron_str.split(','):
            if '*' in field:
                result = True
            elif '-' in field:
                if int(now_val) in range(int(field.split('-')[0]), \
                                         int(field.split('-')[1]) + 1):
                    result = True
            elif int(field) == int(now_val):
                result = True
    except:
        add_message("procedure exception\n{0}".format(traceback.format_exc()))
    
    return result

def worker_cron():
    Timer(1, worker_cron).start()
    
    now = datetime.now()
    
    collection = Collection("inventory")
        
    for prcuuid in collection.find_objuuids(type = "procedure"):
        try:
            procedure = collection.get_object(prcuuid)
            
            if "enabled" not in procedure.object:
                procedure.object["enabled"] = False
                procedure.set()
            
            if "seconds" not in procedure.object:
                procedure.object["seconds"] = "0"
                procedure.set()

            if "minutes" not in procedure.object:
                procedure.object["minutes"] = "*"
                procedure.set()
            
            if "hours" not in procedure.object:
                procedure.object["hours"] = "*"
                procedure.set()
            
            if "dayofmonth" not in procedure.object:
                procedure.object["dayofmonth"] = "*"
                procedure.set()
            
            if "dayofweek" not in procedure.object:
                procedure.object["dayofweek"] = "*"
                procedure.set()
            
            if "year" not in procedure.object:
                procedure.object["year"] = "*"
                procedure.set()
            
            if procedure.object["enabled"] in (True, "true"):
                if eval_cron_field(procedure.object["seconds"], now.second) and \
                   eval_cron_field(procedure.object["minutes"], now.minute) and \
                   eval_cron_field(procedure.object["hours"], now.hour) and \
                   eval_cron_field(procedure.object["dayofmonth"], now.day) and \
                   eval_cron_field(procedure.object["dayofweek"], now.weekday()) and \
                   eval_cron_field(procedure.object["year"], now.year):
                    
                    for hstuuid in procedure.object["hosts"]:
                        queue_procedure(hstuuid, procedure.objuuid, {})
        except:
            add_message("procedure exception\n{0}".format(traceback.format_exc()))

def worker():
    Timer(1, worker).start()
    
    job_lock.acquire()
    
    running_jobs_count = 0
    
    try:    
        # Concurrency conditioning
        for key in list(jobs.keys()):
            try:
                assert int(jobs[key]["host"]["concurrency"]) > 0
            except:
                add_message("invalid host concurrency\n{0}".format(traceback.format_exc()))
                add_message(json.dumps(jobs[key]["host"], indent=4))
                jobs[key]["host"]["concurrency"] = "1"
            
            try:
                assert int(jobs[key]["console"]["concurrency"]) > 0
            except:
                add_message("invalid console concurrency\n{0}".format(traceback.format_exc()))
                add_message(json.dumps(jobs[key]["console"], indent=4))
                jobs[key]["console"]["concurrency"] = "1"

        running_jobs_counts = {}
        for key in list(jobs.keys()):
            running_jobs_counts[jobs[key]["host"]["objuuid"]] = 0
            running_jobs_counts[jobs[key]["console"]["objuuid"]] = 0
            
        for key in list(jobs.keys()):
            if jobs[key]["process"] != None:
                if jobs[key]["process"].is_alive():
                    running_jobs_count += 1
                    running_jobs_counts[jobs[key]["host"]["objuuid"]] += 1
                    running_jobs_counts[jobs[key]["console"]["objuuid"]] += 1
                else:
                    del jobs[key]
                    touch_flag("queueState")
            
        for key in list(jobs.keys()):
            if running_jobs_count < MAX_JOBS:
                if jobs[key]["process"] == None:
                    if running_jobs_counts[jobs[key]["host"]["objuuid"]] < int(jobs[key]["host"]["concurrency"]) and \
                       running_jobs_counts[jobs[key]["console"]["objuuid"]] < int(jobs[key]["console"]["concurrency"]):
                        jobs[key]["process"] = Thread(
                            target = run_procedure,
                            args = (
                                jobs[key]["host"],
                                jobs[key]["procedure"],
                                jobs[key]["console"],
                                jobs[key]["session"],
                                jobs[key]["jobuuid"],
                                jobs[key]["ctruuid"]
                            )
                        )
                        jobs[key]["start time"] = time()
                        jobs[key]["process"].start()
                        running_jobs_count += 1
                        running_jobs_counts[jobs[key]["host"]["objuuid"]] += 1
                        running_jobs_counts[jobs[key]["console"]["objuuid"]] += 1
                        touch_flag("queueState")
    except:
        add_message("queue exception\n{0}".format(traceback.format_exc()))

    job_lock.release()

Thread(target = worker).start()
Thread(target = worker_cron).start()