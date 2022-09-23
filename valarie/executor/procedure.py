#!/usr/bin/python3
"""This module implements functions for scheduling, queuing, and executing
procedures."""
import traceback

from multiprocessing import Process
from threading import Lock, Timer, Thread
from time import time
from datetime import datetime
from imp import new_module
from typing import Dict, List

from valarie.dao.document import Collection
from valarie.dao.utils import get_uuid_str
from valarie.controller import kvstore
from valarie.executor.timers import TIMERS
from valarie.executor.task import TaskError
from valarie.controller import logging
from valarie.controller.config import get_config
from valarie.controller.results import create_result_link
from valarie.controller.inventory import delete_node
from valarie.controller.host import get_hosts

JOBS = {}
JOB_LOCK = Lock()
LAST_WORKER_TIME = time()
DISPLAY_ROW_LOCK = Lock()
OCCUPIED_DISPLAY_ROWS = []

def reserve_display_row() -> int:
    """This function looks for the lowest free display row number and
    adds it to the list of occupied display rows.

    Returns:
        The display row number as an integer.
    """
    try:
        DISPLAY_ROW_LOCK.acquire()
        row_num = 0
        while row_num in OCCUPIED_DISPLAY_ROWS:
            row_num += 1
        OCCUPIED_DISPLAY_ROWS.append(row_num)
    finally:
        DISPLAY_ROW_LOCK.release()
    return row_num

def release_display_row(row_num: int):
    """This function releases display row number by removing it from
    the list of occupied display rows.

    Args:
        row_num:
            The display row number as an integer.
    """
    try:
        DISPLAY_ROW_LOCK.acquire()
        OCCUPIED_DISPLAY_ROWS.remove(row_num)
    finally:
        DISPLAY_ROW_LOCK.release()

def set_job(jobuuid: str, value: Dict):
    """This is a function used to insert a job in the job dictionary.
    This function locks the job dictionary for the insert.

    Args:
        jobuuid:
            UUID of the job.

        value:
            The dictionary of the job.
    """
    try:
        JOB_LOCK.acquire()
        JOBS[jobuuid] = value
    finally:
        JOB_LOCK.release()

def cancel_job(jobuuid: str):
    """This is a function used to cancel a job in the job dictionary.
    Due to deadlocking issues, cancellation only applies to jobs that
    have not been issued a thread yet.

    Args:
        jobuuid:
            UUID of the job.
    """
    try:
        JOB_LOCK.acquire()
        if JOBS[jobuuid]['process'] is None:
            release_display_row(JOBS[jobuuid]["display row"])
            del JOBS[jobuuid]
        elif JOBS[jobuuid]['process'].is_alive():
            JOBS[jobuuid]['process'].terminate()
            release_display_row(JOBS[jobuuid]["display row"])
            del JOBS[jobuuid]
    finally:
        JOB_LOCK.release()

def get_jobs_grid() -> List[Dict]:
    """This is a function used to get a list queued jobs. Each item contains
    a name, runtime, runtime string, and job UUID.

    Returns:
        A list of dictionaries used for the queue list in the front end.
    """
    grid_data = []

    try:
        JOB_LOCK.acquire()

        for jobuuid, job in JOBS.items():
            row = {}

            row["cancellable"] = not isinstance(job["process"], Thread)

            if job["start time"] is not None:
                run_time = time() - job["start time"]
            else:
                run_time = 0

            row["runtimestring"] = "{2}:{1}:{0}".format(
                str(int(run_time % 60)).zfill(2),
                str(int(run_time / 60) % 60).zfill(2),
                str(int(run_time / 3600)).zfill(2)
            )

            row["jobuuid"] = jobuuid
            row["name"] = f'{job["procedure"]["name"]}'
            row["runtime"] = run_time

            if isinstance(job["process"], Process):
                row["runmode"] = "process"
            elif isinstance(job["process"], Thread):
                row["runmode"] = "thread"
            else:
                row["runmode"] = "queued"

            row["displayrow"] = job["display row"]

            grid_data.append(row)
    finally:
        JOB_LOCK.release()

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

    try:
        JOB_LOCK.acquire()

        for jobuuid, job in JOBS.items(): # pylint: disable=unused-variable
            if prcuuid == job["procedure"]["objuuid"] and job["process"] is None:
                hstuuids.append(job["host"]["objuuid"])
    finally:
        JOB_LOCK.release()

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
                    jobuuid = get_uuid_str()

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
                        "ctruuid" : ctruuid,
                        "display row": reserve_display_row()
                    }

                    set_job(jobuuid, job)
        elif temp.object["type"] == "task":
            for current_hstuuid in hstuuids:
                host = inventory.get_object(current_hstuuid)
                if host.object["type"] == "host":
                    jobuuid = get_uuid_str()

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
                        "ctruuid" : ctruuid,
                        "display row": reserve_display_row()
                    }

                    set_job(jobuuid, job)
    else:
        temp.destroy()

# pylint: disable=too-many-locals,too-many-branches,too-many-statements
def run_procedure(
        host_object: Dict,
        procedure_object: Dict,
        console_object: Dict,
        ctruuid: str = None
    ):
    """This is a function runs a procedure using the combination of a host, procedure,
    and console object. Optionally, a controller and job UUID can be specified as well.
    A controller UUID is specified when an executing procedure needs to set controller
    flags in addition to procedure flags to trigger updates in the front end UI.

    Args:
        host_object:
            The host object.

        procedure_object:
            The procedure object.

        console_object:
            The console object.

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
            kvstore.touch(f'procedure-{procedure_object["objuuid"]}')
        if ctruuid:
            kvstore.touch(f'controller-{ctruuid}')


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

        result.object['stop'] = time()
        result.set()

        if host_object["objuuid"] in procedure_object["hosts"]:
            kvstore.touch(f'procedure-{procedure_object["objuuid"]}')
        if ctruuid:
            kvstore.touch(f'controller-{ctruuid}')

    if procedure_status is not None:
        result.object['status'] = procedure_status
        result.set()

        if host_object["objuuid"] in procedure_object["hosts"]:
            kvstore.touch(f'procedure-{procedure_object["objuuid"]}')
        if ctruuid:
            kvstore.touch(f'controller-{ctruuid}')

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
        kvstore.touch('inventoryState')

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
        logging.error(value_error)

    return result

def start_timer():
    """This function creates and starts the procedures timer."""
    TIMERS["procedure worker"] = Timer(1, worker)
    TIMERS["procedure worker"].start()

# pylint: disable=too-many-branches,too-many-statements
def worker():
    """This function is the procedure worker that automatically queues
    procedures that have been enabled to run based on their cron settings.
    This function conditions and evaluates CRON strings. This function also
    conditions and obeys host and console level concurrency limits.
    """
    global LAST_WORKER_TIME # pylint: disable=global-statement
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
            for epoch_time in range(int(LAST_WORKER_TIME), int(time())):
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
                        queue_procedure(hstuuid, procedure.objuuid, None)
                    break

    LAST_WORKER_TIME = time() # pylint: disable=used-before-assignment

    try:
        JOB_LOCK.acquire()

        # Concurrency conditioning
        for key in list(JOBS.keys()):
            try:
                assert int(JOBS[key]["host"]["concurrency"]) > 0
            except (AssertionError, KeyError, ValueError):
                logging.error('invalid host concurrency')
                JOBS[key]["host"]["concurrency"] = "1"

            try:
                assert int(JOBS[key]["console"]["concurrency"]) > 0
            except (AssertionError, KeyError, ValueError):
                logging.error('invalid host concurrency')
                JOBS[key]["console"]["concurrency"] = "1"

        running_jobs_counts = {}
        for key in list(JOBS.keys()):
            running_jobs_counts[JOBS[key]["host"]["objuuid"]] = 0
            running_jobs_counts[JOBS[key]["console"]["objuuid"]] = 0

        for key in list(JOBS.keys()):
            if JOBS[key]["process"] is not None:
                if JOBS[key]["process"].is_alive():
                    running_jobs_count += 1
                    running_jobs_counts[JOBS[key]["host"]["objuuid"]] += 1
                    running_jobs_counts[JOBS[key]["console"]["objuuid"]] += 1
                else:
                    release_display_row(JOBS[key]["display row"])
                    del JOBS[key]

        for key in list(JOBS.keys()):
            if running_jobs_count < int(get_config()["concurrency"]):
                if JOBS[key]["process"] is None:
                    if (
                            running_jobs_counts[JOBS[key]["host"]["objuuid"]] < \
                                int(JOBS[key]["host"]["concurrency"]) and
                            running_jobs_counts[JOBS[key]["console"]["objuuid"]] < \
                                int(JOBS[key]["console"]["concurrency"])
                        ):

                        try:
                            # pylint: disable=line-too-long
                            run_as_process = ('true' in str(JOBS[key]["procedure"]['runasprocess']).lower())
                        except (KeyError, ValueError):
                            run_as_process = False
                        if run_as_process:
                            JOBS[key]["process"] = Process(
                                target=run_procedure,
                                args=(
                                    JOBS[key]["host"],
                                    JOBS[key]["procedure"],
                                    JOBS[key]["console"],
                                    JOBS[key]["ctruuid"]
                                )
                            )
                        else:
                            JOBS[key]["process"] = Thread(
                                target=run_procedure,
                                args=(
                                    JOBS[key]["host"],
                                    JOBS[key]["procedure"],
                                    JOBS[key]["console"],
                                    JOBS[key]["ctruuid"]
                                )
                            )

                        JOBS[key]["start time"] = time()
                        JOBS[key]["process"].start()

                        running_jobs_count += 1
                        running_jobs_counts[JOBS[key]["host"]["objuuid"]] += 1
                        running_jobs_counts[JOBS[key]["console"]["objuuid"]] += 1

        kvstore.touch("queueState")
    finally:
        JOB_LOCK.release()
        start_timer()
