#!/usr/bin/python

from valarie.dao.document import Collection

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
        self.send("{0}\\n".format(file.file.read()))'''

def create_console(parent_objuuid, name = "New Console", objuuid = None):
    collection = Collection("inventory")
    console = collection.get_object(objuuid)
    console.object = {
        "type" : "console",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "body" : CONSOLE_PROTO_BODY,
        "icon" : "/images/console_icon.png",
        "concurrency" : 1,
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/ajax_delete",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit console",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            },
            "copy" : {
                "label" : "Copy",
                "action" : {
                    "method" : "copy node",
                    "route" : "inventory/ajax_copy_object",
                    "params" : {
                        "objuuid" : console.objuuid
                    }
                }
            }
        }
    }
    
    console.set()
    
    parent = collection.get_object(parent_objuuid)
    parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
    parent.set()
    
    return console

def get_consoles():
    collection = Collection("inventory")
    
    console_objects = []
    
    for object in collection.find(type = "console"):
        console_objects.append(object.object)
        
    return console_objects