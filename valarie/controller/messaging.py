#!/usr/bin/python3

import cherrypy
import json

from threading import Lock
from time import time, strftime, localtime
from copy import deepcopy

message_lock = Lock()
messages = {
    "messages" : []
}

def add_message(message, timestamp = None):
    if not timestamp:
        timestamp = time()
    
    cherrypy.log(strftime('%H:%M:%S', localtime(timestamp)), str(message))
    
    message_lock.acquire()
    messages["messages"] = [{"message" : deepcopy(message), "timestamp" : strftime('%H:%M:%S', localtime(timestamp))}] + messages["messages"][:49]
    message_lock.release()

def get_messages():
    message_lock.acquire()
    temp = deepcopy(messages)
    message_lock.release()
    return temp

class Messaging(object):
    @cherrypy.expose
    def add_message(self, message, timestamp):
        add_message(message, timestamp)
        return json.dumps({})
    
    @cherrypy.expose
    def add_message(self, message):
        add_message(message)
        return json.dumps({})
    
    @cherrypy.expose
    def get_messages(self):
        return json.dumps(get_messages())
