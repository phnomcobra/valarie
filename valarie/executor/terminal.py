#!/usr/bin/python

CLI_TIME_OUT = 5 * 60
RECV_TIME_OUT = 60

import traceback

from threading import Timer
from imp import new_module
from time import time

from valarie.controller.messaging import add_message
from valarie.dao.document import Collection
from valarie.dao.utils import sucky_uuid

cli_sessions = {}

class ErrorConsole:
    def __init__(self, message):
        self.__buffer = message
    
    def send(self, input_buffer):
        pass
    
    def recv(self):
        output_buffer = self.__buffer
        self.__buffer = ''
        return output_buffer

def send(ttyuuid, buffer):
    try:
        cli_sessions[ttyuuid]["contact"] = time()
        cli_sessions[ttyuuid]["console"].send(buffer)
    except:
        add_message(traceback.format_exc())

def recv(ttyuuid):
    try:
        cli_sessions[ttyuuid]["contact"] = time()
        return cli_sessions[ttyuuid]["console"].recv()
    except:
        add_message(traceback.format_exc())
        return traceback.format_exc()

def write_file(ttyuuid, file):
    try:
        cli_sessions[ttyuuid]["console"].putf(file)
        cli_sessions[ttyuuid]["contact"] = time()
    except:
        add_message(traceback.format_exc())
        
def create_session(hstuuid, session):
    try:
        ttyuuid = sucky_uuid()
       
        inventory = Collection("inventory")
        host = inventory.get_object(hstuuid)
        tempmodule = new_module("tempmodule")
        exec(inventory.get_object(host.object["console"]).object["body"], tempmodule.__dict__)
        
        if "send" not in dir(tempmodule.Console):
            raise Exception("send method not present in console object!")
        
        if "recv" not in dir(tempmodule.Console):
            raise Exception("recv method not present in console object!")
        
        cli_sessions[ttyuuid] = {}
        cli_sessions[ttyuuid]["console"] = tempmodule.Console(session = session, host = host.object)
        cli_sessions[ttyuuid]["contact"] = time()
    except:
        cli_sessions[ttyuuid] = {}
        cli_sessions[ttyuuid]["console"] = ErrorConsole(traceback.format_exc())
        cli_sessions[ttyuuid]["contact"] = time()
        
        add_message(traceback.format_exc())
    finally:
        Timer(60, time_out_worker, args = (ttyuuid,)).start()
        
        return ttyuuid

def destroy_session(ttyuuid):
    try:
        try:
            cli_sessions[ttyuuid]["console"].close()
        except:
            add_message(traceback.format_exc())
        finally:
            del cli_sessions[ttyuuid]
    except Exception:
        add_message(traceback.format_exc())
        
def time_out_worker(ttyuuid):
    try:
        if time() - cli_sessions[ttyuuid]["contact"] > CLI_TIME_OUT:
            add_message("terminal model: ttyuuid {0} closed due to inactivity".format(ttyuuid))
            destroy_session(ttyuuid)
        else:
            Timer(60, time_out_worker, args = (ttyuuid,)).start()
    except:
        add_message(traceback.format_exc())