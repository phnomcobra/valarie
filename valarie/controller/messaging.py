#!/usr/bin/python

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
    
    message_lock.acquire()
    messages["messages"] = [{"message" : deepcopy(message), "timestamp" : strftime('%H:%M:%S', localtime(timestamp))}] + messages["messages"][:49]
    message_lock.release()

def get_messages():
    message_lock.acquire()
    temp = deepcopy(messages)
    message_lock.release()
    return temp

class Messaging(object):
    def __init__(self):
        self.messages = {"messages":[]}
    
    @cherrypy.expose
    def ajax_add_message(self, message, timestamp):
        add_message(message, timestamp)
        return json.dumps({})
    
    @cherrypy.expose
    def ajax_add_message(self, message):
        add_message(message)
        return json.dumps({})
    
    @cherrypy.expose
    def ajax_get_messages(self):
        return json.dumps(get_messages())