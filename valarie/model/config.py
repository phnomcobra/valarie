#!/usr/bin/python

from valarie.dao.document import Collection

CONFIG_OBJUUID = "bec8aa75-575e-4014-961c-d2df363c66bf"
TASK_PROTO_OBJUUID = "4d22259a-8000-49c7-bb6b-cf8526dbff70"
CONSOLE_PROTO_OBJUUID = "d64e5c18-2fe8-495b-ace1-a3f0321b1629"
SETTINGS_CONTAINER_OBJUUID = "bcde4d54-9456-4b09-9bff-51022e799b30"

CONSOLE_PROTO_BODY = '''#!/usr/bin/python

from subprocess import Popen, PIPE

class Console:
    def __init__(self, **kargs):
        self.__buffer = 'Local Host Test Terminal: '
    
    def get_remote_host(self):
        return "127.0.0.1"
    
    def system(self, command, return_tuple = False, sudo_command = True):
        process = Popen(command, shell = True, stdout = PIPE, stderr = PIPE)
        output_buffer, stderr_buffer = process.communicate()
        status = process.returncode
        
        if return_tuple:
            return status, output_buffer, stderr_buffer
        elif 0 != int(status):
            return '{0}<font color="red"><br>{1}</font><br>'.format(output_buffer, stderr_buffer)
        else:
            return output_buffer
    
    def send(self, input_buffer):
        self.__buffer += input_buffer
        pass
    
    def recv(self):
        output_buffer = self.__buffer
        self.__buffer = ''
        return output_buffer
    
    def putf(self, file):
        self.send("filename: {0}\\n".format(file.filename))
        self.send("{0}\\n".format(file.file.read()))
'''

TASK_PROTO_BODY = '''#!/usr/bin/python

import traceback

class Task:
    def __init__(self):
        self.output = []
        self.status = STATUS_NOT_EXECUTED

    def execute(self, cli):
        try:
            status, stdout, stderr = cli.system("whoami", return_tuple = True)
            if status:
                self.output.append(str(stderr))
                self.status = STATUS_FAILURE
            else:
                self.output.append(str(stdout))
                self.status = STATUS_SUCCESS
        except:
            self.output.append(traceback.format_exc())
            self.status = STATUS_EXCEPTION

        return self.status
'''

def get_config():
    return Collection("inventory").get_object(CONFIG_OBJUUID).object

def get_host():
    return Collection("inventory").get_object(CONFIG_OBJUUID).object["host"]

def get_port():
    return int(Collection("inventory").get_object(CONFIG_OBJUUID).object["port"])

def create_config():
    collection = Collection("inventory")

    config = collection.get_object(CONFIG_OBJUUID)

    config.object = {
        "type" : "config",
        "parent" : SETTINGS_CONTAINER_OBJUUID,
        "concurrency" : 20,
        "host" : "0.0.0.0",
        "port" : 8080,
        "brand" : "valarie",
        "banner" : "<h1>Valarie</h1>",
        "title" : "Valarie",
        "restartcmd" : "service valarie restart",
        "children" : [],
        "name" : "Configuration",
        "icon" : "/images/config_icon.png",
        "context" : {
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit configuration",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : CONFIG_OBJUUID
                    }
                }
            },
            "restart" : {
                "label" : "Restart",
                "action" : {
                    "method" : "restart valarie",
                    "route" : "general/ajax_restart",
                    "params" : {}
                }
            }
        }
    }
    
    config.set()
    
    return config

def get_console_template():
    return Collection("inventory").get_object(CONSOLE_PROTO_OBJUUID).object["body"]

def create_console_template():
    collection = Collection("inventory")

    console = collection.get_object(CONSOLE_PROTO_OBJUUID)

    console.object = {
        "type" : "console",
        "parent" : SETTINGS_CONTAINER_OBJUUID,
        "body" : CONSOLE_PROTO_BODY,
        "children" : [],
        "name" : "Console Template",
        "icon" : "/images/config_icon.png",
        "concurrency" : 1,
        "context" : {
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit console",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : CONSOLE_PROTO_OBJUUID
                    }
                }
            }
        }
    }
    
    console.set()
    
    return console

def get_task_template():
    return Collection("inventory").get_object(TASK_PROTO_OBJUUID).object["body"]

def create_task_template():
    collection = Collection("inventory")
    
    task = collection.get_object(TASK_PROTO_OBJUUID)
    
    task.object = {
        "type" : "task",
        "parent" : SETTINGS_CONTAINER_OBJUUID,
        "children" : [],
        "name" : "Task Template",
        "body" : TASK_PROTO_BODY,
        "hosts" : [],
        "icon" : "/images/config_icon.png",
        "context" : {
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit task",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            }
        }
    }
    
    task.set()
    
    return task


def create_settings_container():
    collection = Collection("inventory")
    
    container = collection.get_object(SETTINGS_CONTAINER_OBJUUID)
    
    container.object = {
        "type" : "container",
        "parent" : "#",
        "children" : [
            TASK_PROTO_OBJUUID,
            CONSOLE_PROTO_OBJUUID,
            SETTINGS_CONTAINER_OBJUUID
        ],
        "name" : "Settings",
        "icon" : "images/tree_icon.png",
        "context" : {
        }
    }
    
    container.set()
    
    return container
