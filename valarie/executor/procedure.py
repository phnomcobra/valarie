#!/usr/bin/python3
"""This module implements functions for scheduling, queuing, and executing
procedures."""
import traceback

from threading import Lock, Thread, Timer
from time import time
from datetime import datetime
from imp import new_module
from typing import Any, Dict, List

from valarie.dao.document import Collection
from valarie.dao.utils import sucky_uuid
from valarie.controller import kvstore as kv
from valarie.router.messaging import add_message
from valarie.executor.timers import timers
from valarie.executor.task import TaskError
from valarie.controller.config import get_config
from valarie.controller.results import create_result_link
from valarie.controller.inventory import delete_node
from valarie.controller.host import get_hosts

jobs = {}
job_lock = Lock()

def update_job(jobuuid: str, key: str, value: Any):
    """This is a function used to update a key in a job.
    This function locks the job dictionary for the update.

    Args:
        jobuuid:
            UUID of the job.

        key:
            The key to update.

        value:
            The value to set the key to.

    """
    job_lock.acquire()
    jobs[jobuuid][key] = value
    job_lock.release()
    kv.touch("queueState")

def set_job(jobuuid: str, value: Dict):
    """This is a function used to insert a job in the job dictionary.
    This function locks the job dictionary for the insert.

    Args:
        jobuuid:
            UUID of the job.

        value:
            The dictionary of the job.
    """
    job_lock.acquire()
    jobs[jobuuid] = value
    job_lock.release()
    kv.touch("queueState")

def get_jobs_grid() -> List[Dict]:
    """This is a function used to get a list queued jobs. Each item contains
    a name, host, hostname, progress indicator status, and runtime.

    Returns:
        A list of dictionaries used for the queue list in the front end.
    """
    grid_data = []
    job_lock.acquire()

    for jobuuid, job in jobs.items(): # pylint: disable=unused-variable
        row = {}

        if job["start time"] is None:
            run_time = 0
        else:
            run_time = time() - job["start time"]

        row["name"] = job["procedure"]["name"]
        row["hostname"] = job["host"]["name"]
        row["host"] = job["host"]["host"]
        row["progress"] = job["progress"]
        row["status"] = "Queued" if job["start time"] is None else "Running"
        row["runtime"] = "{2}:{1}:{0}".format(
            str(int(run_time % 60)).zfill(2),
            str(int(run_time / 60) % 60).zfill(2),
            str(int(run_time / 3600)).zfill(2)
        )

        grid_data.append(row)

    job_lock.release()

    # sort list by progress
    # pylint: disable=consider-using-enumerate
    for i in range(0, len(grid_data)):
        for j in range(i, len(grid_data)):
            if grid_data[i]["progress"] < grid_data[j]["progress"]:
                grid_data[i], grid_data[j] = grid_data[j], grid_data[i]

    return grid_data

def get_queued_hosts(prcuuid: str) -> List[str]:
    """This is a function used to get a list queued hosts for a particular
    procedure. This function is used to measure concurrency and prevent
    a procedure from being queued multiple times for the same host. The job
    list is locked while host UUIDs are accumulated.

    Returns:
        A list of host UUIDs.
    """
    hstuuids = []

    job_lock.acquire()

    for jobuuid, job in jobs.items(): # pylint: disable=unused-variable
        if prcuuid == job["procedure"]["objuuid"] and job["process"] is None:
            hstuuids.append(job["host"]["objuuid"])

    job_lock.release()

    return hstuuids

def queue_procedure(hstuuid: str, prcuuid: str, ctruuid: str = None):
    """This is a function queues a procedure for execution with a particular host
    object. Optionally, a controller can be specified as well. This is done when an
    executing procedure needs to set controller flags in addition to procedure flags
    to trigger updates in the front end UI.

    A task UUID may be supplied for the the procedure UUID. When this occurs, a
    temporary procedure is created to encapsulate the task. Results are not persisted
    to the inventory and there is no way to alter retention.

    Args:
        hstuuid:
            The UUID of the host object.

        prcuuid:
            The UUID of the procedure object.

        ctruuid:
            The UUID of the controller object.
    """
    inventory = Collection("inventory")

    # Discover Nested Hosts
    discovered_hstuuids = []
    grpuuids = []
    get_hosts(hstuuid, discovered_hstuuids, grpuuids, inventory)

    # Exclude Hosts Already Queued
    queued_hstuuids = get_queued_hosts(prcuuid)
    hstuuids = []
    for discovered_hstuuid in discovered_hstuuids:
        if discovered_hstuuid not in queued_hstuuids:
            hstuuids.append(discovered_hstuuid)

    temp = inventory.get_object(prcuuid)

    if "type" in temp.object:
        if temp.object["type"] == "procedure":
            for current_hstuuid in hstuuids:
                host = inventory.get_object(current_hstuuid)

                if host.object["type"] == "host":
                    jobuuid = sucky_uuid()

                    console = inventory.get_object(host.object["console"])

                    job = {
                        "jobuuid" : jobuuid,
                        "host" : host.object,
                        "console" : console.object,
                        "procedure" : temp.object,
                        "process" : None,
                        "queue time" : time(),
                        "start time" : None,
                        "progress" : 0,
                        "ctruuid" : ctruuid
                    }

                    set_job(jobuuid, job)
        elif temp.object["type"] == "task":
            for current_hstuuid in hstuuids:
                host = inventory.get_object(current_hstuuid)
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
                            "description" : "This is a synthetic procedure used for "\
                                            "encapsulating tasks for use with controller objects.",
                            "resultexpirationperiod" : 3600,
                            "resultinventoryupdate" : False,
                            "resultoverwrite" : True,
                            "resultlinkenable" : False,
                        },
                        "process" : None,
                        "queue time" : time(),
                        "start time" : None,
                        "progress" : 0,
                        "ctruuid" : ctruuid
                    }

                    set_job(jobuuid, job)
    else:
        temp.destroy()

# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def run_procedure(
        host_object: Dict,
        procedure_object: Dict,
        console_object: Dict,
        jobuuid: str = None,
        ctruuid: str = None
    ):
    """This is a function runs a procedure using the combination of a host, procedure,
    and console object. Optionally, a controller and job UUID can be specified as well.
    A controller UUID is specified when an executing procedure needs to set controller
    flags in addition to procedure flags to trigger updates in the front end UI. A job
    UUID is specified when a procedure is being run from a job and needs to update a
    job's progress key.

    Args:
        host_object:
            The host object.

        procedure_object:
            The procedure object.

        console_object:
            The console object.

        jobuuid:
            The UUID of the job object.

        ctruuid:
            The UUID of the controller object.
    """
    inventory = Collection("inventory")
    results = Collection("results")

    try:
        result_overwrite = ('true' in str(procedure_object['resultoverwrite']).lower())
    except (KeyError, ValueError):
        result_overwrite = True
    if result_overwrite:
        for result in results.find(
                hstuuid=host_object["objuuid"],
                prcuuid=procedure_object["objuuid"]
            ):
            if "linkuuid" in result.object:
                delete_node(result.object['linkuuid'])
            result.destroy()

    result = results.get_object()

    result.object['start'] = time()
    result.object["output"] = []

    status_code_body = ""
    status_data = {}

    for status in inventory.find(type="status"):
        try:
            status_code_body += f"""{status.object["alias"]}=int('{status.object["code"]}')\n"""
            status_data[int(status.object["code"])] = status.object
        except (KeyError, ValueError):
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

    tskuuids = procedure_object["tasks"]

    for seq_num, tskuuid in enumerate(tskuuids):
        task_result = {}
        task_result["name"] = inventory.get_object(tskuuid).object["name"]
        task_result["start"] = None
        task_result["stop"] = None
        task_result["tskuuid"] = tskuuid

        try:
            # pylint: disable=exec-used
            exec(
                f'{inventory.get_object(tskuuid).object["body"]}\n{status_code_body}',
                tempmodule.__dict__
            )
            task = tempmodule.Task()
        except: # pylint: disable=bare-except
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
        except KeyError:
            task_result['status'] = {"code": task.status}

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
            kv.touch(f'procedure-{procedure_object["objuuid"]}')
        if ctruuid:
            kv.touch(f'controller-{ctruuid}')


    procedure_status = None

    try:
        # pylint: disable=exec-used
        exec(console_object["body"], tempmodule.__dict__)
        cli = tempmodule.Console(host=host_object)
    except: # pylint: disable=bare-except
        result.object["output"] += traceback.format_exc().split("\n")

    for seq_num, tskuuid in enumerate(tskuuids):
        task_result = {}
        task_result["name"] = inventory.get_object(tskuuid).object["name"]
        task_result["start"] = None
        task_result["stop"] = None

        try:
            # pylint: disable=exec-used
            exec(
                f'{inventory.get_object(tskuuid).object["body"]}\n{status_code_body}',
                tempmodule.__dict__
            )
            task = tempmodule.Task()

            if continue_procedure:
                task_result["start"] = time()

                try:
                    task.execute(cli)
                except: # pylint: disable=bare-except
                    task = TaskError(tskuuid)

                task_result["stop"] = time()
        except: # pylint: disable=bare-except
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
                continue_flag = procedure_object[f"continue {task.status}"]

                if continue_flag == 'false':
                    continue_flag = False
                if not continue_flag:
                    continue_procedure = False
            except KeyError:
                continue_procedure = False
        except KeyError:
            task_result['status'] = {"code": task.status}
            continue_procedure = False

        result.object['tasks'][seq_num] = task_result

        if winning_status is None:
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
            kv.touch(f'procedure-{procedure_object["objuuid"]}')
        if ctruuid:
            kv.touch(f'controller-{ctruuid}')

    if procedure_status is not None:
        result.object['status'] = procedure_status
        result.set()

        if host_object["objuuid"] in procedure_object["hosts"]:
            kv.touch(f'procedure-{procedure_object["objuuid"]}')
        if ctruuid:
            kv.touch(f'controller-{ctruuid}')

    try:
        result_link_enabled = ('true' in str(procedure_object['resultlinkenable']).lower())
    except (KeyError, ValueError):
        result_link_enabled = False
    if result_link_enabled:
        stop_time_str = datetime.fromtimestamp(int(result.object['stop']))

        link = create_result_link(
            procedure_object['objuuid'],
            f"{host_object['name']}:{stop_time_str}:{result.object['status']['abbreviation']}",
        )
        link.object['hstuuid'] = host_object['objuuid']
        link.object['prcuuid'] = procedure_object["objuuid"]
        link.object['resuuid'] = result.object['objuuid']
        link.set()

        result.object['linkuuid'] = link.object['objuuid']
        result.set()

    try:
        update_inventory = ('true' in str(procedure_object['resultinventoryupdate']).lower())
    except (KeyError, ValueError):
        update_inventory = False
    if update_inventory:
        kv.touch('inventoryState')

    return result.object

def eval_cron_field(cron_str: str, now_val: int) -> bool:
    """This function evaluates a CRON field and returns true or false depending
    on if there is a match. The function matches by '*', range "2-5", or integer.

    Args:
        cron_str:
            The CRON string being evaluated.

        now_val:
            The now value being matched against.

    Returns:
        A bool indicated a match or not.
    """
    result = False

    try:
        for field in cron_str.split(','):
            if '*' in field:
                result = True
            elif '-' in field:
                if now_val in range(
                        int(field.split('-')[0]),
                        int(field.split('-')[1]) + 1
                    ):
                    result = True
            elif int(field) == now_val:
                result = True
    except ValueError as value_error:
        add_message(str(value_error))

    return result

# pylint: disable=too-many-branches,too-many-statements
def worker():
    """This function is the procedure worker that automatically queues
    procedures that have been enabled to run based on their cron settings.
    This function conditions and evaluates CRON strings. This function also
    conditions and obeys host and console level concurrency limits.
    """
    global last_worker_time
    running_jobs_count = 0

    inventory = Collection("inventory")

    for prcuuid in inventory.find_objuuids(type="procedure"):
        procedure = inventory.get_object(prcuuid)

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
            for epoch_time in range(int(last_worker_time), int(time())):
                now = datetime.fromtimestamp(epoch_time).now()
                # pylint: disable=too-many-boolean-expressions
                if (
                        eval_cron_field(procedure.object["seconds"], now.second) and
                        eval_cron_field(procedure.object["minutes"], now.minute) and
                        eval_cron_field(procedure.object["hours"], now.hour) and
                        eval_cron_field(procedure.object["dayofmonth"], now.day) and
                        eval_cron_field(procedure.object["dayofweek"], now.weekday()) and
                        eval_cron_field(procedure.object["year"], now.year)
                    ):
                    for hstuuid in procedure.object["hosts"]:
                        queue_procedure(hstuuid, procedure.objuuid, {})
                    break

    last_worker_time = time()

    job_lock.acquire()

    # Concurrency conditioning
    for key in list(jobs.keys()):
        try:
            assert int(jobs[key]["host"]["concurrency"]) > 0
        except (AssertionError, KeyError, ValueError):
            add_message(f"invalid host concurrency\n{traceback.format_exc()}")
            jobs[key]["host"]["concurrency"] = "1"

        try:
            assert int(jobs[key]["console"]["concurrency"]) > 0
        except (AssertionError, KeyError, ValueError):
            add_message(f"invalid console concurrency\n{traceback.format_exc()}")
            jobs[key]["console"]["concurrency"] = "1"

    running_jobs_counts = {}
    for key in list(jobs.keys()):
        running_jobs_counts[jobs[key]["host"]["objuuid"]] = 0
        running_jobs_counts[jobs[key]["console"]["objuuid"]] = 0

    for key in list(jobs.keys()):
        if jobs[key]["process"] is not None:
            if jobs[key]["process"].is_alive():
                running_jobs_count += 1
                running_jobs_counts[jobs[key]["host"]["objuuid"]] += 1
                running_jobs_counts[jobs[key]["console"]["objuuid"]] += 1
            else:
                del jobs[key]
                kv.touch("queueState")

    for key in list(jobs.keys()):
        if running_jobs_count < int(get_config()["concurrency"]):
            if jobs[key]["process"] is None:
                if (
                        running_jobs_counts[jobs[key]["host"]["objuuid"]] < \
                            int(jobs[key]["host"]["concurrency"]) and
                        running_jobs_counts[jobs[key]["console"]["objuuid"]] < \
                            int(jobs[key]["console"]["concurrency"])
                    ):
                    jobs[key]["process"] = Thread(
                        target=run_procedure,
                        args=(
                            jobs[key]["host"],
                            jobs[key]["procedure"],
                            jobs[key]["console"],
                            jobs[key]["jobuuid"],
                            jobs[key]["ctruuid"]
                        )
                    )
                    jobs[key]["start time"] = time()
                    jobs[key]["process"].start()
                    running_jobs_count += 1
                    running_jobs_counts[jobs[key]["host"]["objuuid"]] += 1
                    running_jobs_counts[jobs[key]["console"]["objuuid"]] += 1
                    kv.touch("queueState")

    job_lock.release()

    timers["procedure worker"] = Timer(1, worker)
    timers["procedure worker"].start()

last_worker_time = time()

timers["procedure worker"] = Timer(1, worker)
timers["procedure worker"].start()
