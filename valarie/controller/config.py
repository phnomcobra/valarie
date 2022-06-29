#!/usr/bin/python3
"""This module sets and exposes the default values for configuration and templates."""
from typing import Dict

from valarie.dao.document import Collection, Object

CONFIG_OBJUUID = "bec8aa75-575e-4014-961c-d2df363c66bf"
TASK_PROTO_OBJUUID = "4d22259a-8000-49c7-bb6b-cf8526dbff70"
CONSOLE_PROTO_OBJUUID = "d64e5c18-2fe8-495b-ace1-a3f0321b1629"
SETTINGS_CONTAINER_OBJUUID = "bcde4d54-9456-4b09-9bff-51022e799b30"

CONSOLE_PROTO_BODY = '''#!/usr/bin/python3

from subprocess import Popen, PIPE

class Console:
    def get_remote_host(self):
        return "127.0.0.1"

    def system(self, command, return_tuple=False, sudo_command=True):
        process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        output_buffer, stderr_buffer = process.communicate()
        status = process.returncode

        if return_tuple:
            return status, output_buffer, stderr_buffer
        elif 0 != int(status):
            return f'{output_buffer}<font color="red"><br>{stderr_buffer}</font><br>'
        else:
            return output_buffer
'''

TASK_PROTO_BODY = '''#!/usr/bin/python3

import traceback

class Task:
    def __init__(self):
        self.output = []
        self.status = STATUS_NOT_EXECUTED

    def execute(self, cli):
        try:
            status, stdout, stderr = cli.system("whoami", return_tuple=True)
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

def get_config() -> Dict:
    """This function gets the configuration object in the inventory.

    Returns:
        A document object dictionary.
    """
    return Collection("inventory").get_object(CONFIG_OBJUUID).object

def get_host() -> str:
    """This function gets the host the web server will serve on.

    Returns:
        A host string.
    """
    return Collection("inventory").get_object(CONFIG_OBJUUID).object["host"]

def get_port() -> int:
    """This function gets the port the web server will serve on.

    Returns:
        A port number as an int.
    """
    return int(Collection("inventory").get_object(CONFIG_OBJUUID).object["port"])

def create_config() -> Object:
    """This function creates and returns the configuration object
    in the inventory.

    Returns:
        The document object for the configuration settings.
    """
    inventory = Collection("inventory")

    config = inventory.get_object(CONFIG_OBJUUID)

    config.object = {
        "type" : "config",
        "parent" : SETTINGS_CONTAINER_OBJUUID,
        "concurrency" : 20,
        "host" : "0.0.0.0",
        "port" : 8080,
        "brand" : "valarie",
        "restartcmd" : "service valarie restart",
        "children" : [],
        "name" : "Configuration",
        "icon" : "/images/config_icon.png",
        "context" : {
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit configuration",
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : CONFIG_OBJUUID
                    }
                }
            },
            "restart" : {
                "label" : "Restart",
                "action" : {
                    "method" : "restart valarie",
                    "route" : "general/restart",
                    "params" : {}
                }
            }
        }
    }

    config.set()

    return config

def get_console_template() -> str:
    """This function gets the console template.

    Returns:
        String of the console template.
    """
    return Collection("inventory").get_object(CONSOLE_PROTO_OBJUUID).object["body"]

def create_console_template() -> Object:
    """This function creates and returns the console template object
    in the inventory using the default console body.

    Returns:
        The document object for the console.
    """
    inventory = Collection("inventory")

    console = inventory.get_object(CONSOLE_PROTO_OBJUUID)

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
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : CONSOLE_PROTO_OBJUUID
                    }
                }
            }
        }
    }

    console.set()

    return console

def get_task_template() -> str:
    """This function gets the task template.

    Returns:
        String of the task template.
    """
    return Collection("inventory").get_object(TASK_PROTO_OBJUUID).object["body"]

def create_task_template() -> Object:
    """This function creates and returns the task template object
    in the inventory using the default task body.

    Returns:
        The document object for the task.
    """
    inventory = Collection("inventory")

    task = inventory.get_object(TASK_PROTO_OBJUUID)

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
                    "route" : "inventory/get_object",
                    "params" : {
                        "objuuid" : task.objuuid
                    }
                }
            }
        }
    }

    task.set()

    return task


def create_settings_container() -> Object:
    """This function creates and returns settings container for the
    inventory.

    Returns:
        The document object for the container.
    """
    inventory = Collection("inventory")

    container = inventory.get_object(SETTINGS_CONTAINER_OBJUUID)

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
