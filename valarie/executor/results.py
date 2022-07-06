#!/usr/bin/python3
"""This module implements the results worker."""
from threading import Timer
from time import time

from valarie.executor.timers import TIMERS
from valarie.dao.document import Collection
from valarie.controller.inventory import delete_node
from valarie.controller import kvstore as kv

def start_timer():
    """This function creates and starts the results timer."""
    TIMERS["results worker"] = Timer(60, worker)
    TIMERS["results worker"].start()

def worker():
    """This is a worker function used to process expiration of results
    and result links."""
    start_timer()

    results = Collection("results")
    inventory = Collection('inventory')
    refresh_inventory = False

    for objuuid in results.list_objuuids():
        result = results.get_object(objuuid)
        try:
            procedure = inventory.get_object(result.object['procedure']['objuuid'])

            try:
                expiration_period = int(procedure.object['resultexpirationperiod'])
            except (KeyError, ValueError):
                expiration_period = 3600

            try:
                update_inventory = (
                    'true' in str(procedure.object['resultinventoryupdate']).lower()
                )
            except (KeyError, ValueError):
                update_inventory = False

            if time() - result.object["start"] > expiration_period and expiration_period != 0:
                if "linkuuid" in result.object:
                    delete_node(result.object['linkuuid'])
                    if update_inventory:
                        refresh_inventory = True

                result.destroy()
        except KeyError:
            result.destroy()

    if refresh_inventory:
        kv.touch("inventoryState")
