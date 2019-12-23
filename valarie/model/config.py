#!/usr/bin/python

from valarie.dao.document import Collection

CONFIG_OBJUUID = "bec8aa75-575e-4014-961c-d2df363c66bf"
TASK_PROTO_OBJUUID = "4d22259a-8000-49c7-bb6b-cf8526dbff70"
CONSOLE_PROTO_OBJUUID = "d64e5c18-2fe8-495b-ace1-a3f0321b1629"
PUBLIC_KEY_OBJUUID = "e556ad0c-46a1-4ade-be1c-826cf615deca"
PRIVATE_KEY_OBJUUID = "05490097-956c-4ccb-b817-dbe76ca3265e"
SETTINGS_CONTAINER_OBJUUID = "bcde4d54-9456-4b09-9bff-51022e799b30"

# This is an invalid, self-signed key pair!
PUBLIC_KEY_BODY = '''-----BEGIN CERTIFICATE-----
MIIGBTCCA+2gAwIBAgIJAJ4UmiHXQLcdMA0GCSqGSIb3DQEBBQUAMIGYMQswCQYD
VQQGEwJVUzENMAsGA1UECAwET2hpbzERMA8GA1UEBwwIQ29sdW1idXMxDTALBgNV
BAoMBERJU0ExDzANBgNVBAsMBlNFTDY0MzEYMBYGA1UEAwwPSnVzdGluIERpZXJr
aW5nMS0wKwYJKoZIhvcNAQkBFh5qdXN0aW4ubC5kaWVya2luZy5jaXZAbWFpbC5t
aWwwHhcNMTcxMTI4MTQ0MjMxWhcNMTgxMTI4MTQ0MjMxWjCBmDELMAkGA1UEBhMC
VVMxDTALBgNVBAgMBE9oaW8xETAPBgNVBAcMCENvbHVtYnVzMQ0wCwYDVQQKDARE
SVNBMQ8wDQYDVQQLDAZTRUw2NDMxGDAWBgNVBAMMD0p1c3RpbiBEaWVya2luZzEt
MCsGCSqGSIb3DQEJARYeanVzdGluLmwuZGllcmtpbmcuY2l2QG1haWwubWlsMIIC
IjANBgkqhkiG9w0BAQEFAAOCAg8AMIICCgKCAgEA7rfvOi1zsfIqRzG6QGhZUf83
AEkzXuUFHwtt5a8VGK7APV0ZKLdABFe8WCBwFqKkap88NI3ET9zWDvYj59uAjZ3R
la8pujtnd0LkKyiZExOb7gt8RY3ayHIvngYM0YtYkHrj3iJKBr+NsIj8D4meEI2T
UYix7Sfeytn1N2J5DDHtyequjqBD5Qhzv5R9deFCesQqN2mOy6eM9Eqg2YMuHw3x
ou0f13oTd16jCCCasDI+Q3F14lJNZYdH8+UVJPIt7jnsXtsEdC3nus2MyzKjtUd6
3zevkq840q8wejNaZWp1v8bdtCqevW95pjmyLnFBrwot9MYTUhYxt33vpGEeK+jN
3/DUn11BvmO20lyxCakclE/KReLxtPTHObusgebGNj9ZJhvWcRWeEXJ2wO94ZSlF
+9FE9K/LWkTZvjzThEo8DjlpumWB79Cd0A5nsJYxeprJD9vkg1z2StNcl2MTiHA/
MDRhY0/YniUlCiNneo9xmXC7ehfwM6Q/1rRfppIGM9rqXtfefEKeakTODmrG8g21
faXQasp/dqKVbDBkzgCDdGQbmnomTvlhz5dx7DDZc9kmauhKvyyAEapka+/uc/3R
toMKD18wq9oDnVb/s6A9OAzcfLF88xH4mEB0chJsf3UsnLk/1X+ZZBsJt53q48ua
dikL/pv7J9wpOqugBnsCAwEAAaNQME4wHQYDVR0OBBYEFGot4JXo67d/JBZNbArG
/0uFmwClMB8GA1UdIwQYMBaAFGot4JXo67d/JBZNbArG/0uFmwClMAwGA1UdEwQF
MAMBAf8wDQYJKoZIhvcNAQEFBQADggIBAOqgdGSzg214PNm1JhB2dxNQzDiVCAVQ
NwFRdhaMoLoJqCKyYKe5kQe1C4CxippOwcVsFjuKJYesdVOmTJYXdodwLpu2TYIx
4G3DhVp1oxULXwif2SDGxHqfaWo/D85TG8g6BdLprXYzdT1wRHM15rDudCHnc8fJ
pc9B2keygIgFMinl5N6MKrG53B1KgRRdNfWcLL1+WDNTj6NzOWoVke33Bg28vxAl
bkdto01gmbVuXl2YYuV8ijE/3P0navgvxQvLJeE+07AqBhnWewzIQiClDuf3vh5X
cEY7qPhbkLlNM2nlAn26x7ane8N+/xjwZL0KHMUXbhTK7iCe0t0CzpQAfMh1yZ84
G1AGqo4L2AGEOwd2dWG30BPh8VR79Ds7zEZzaCAcgtdI5QWXdsqn37q0masdaeSt
upJ1mquzpTe4P8hpzNAcGh21YeqZGHeXR+sz91B6J2UnGVH78LImlBB4LF0FggPy
ckD64EbIuvMd4SONDUeBhjq2JGYeRbmcmnCDs4eDSRkePjPgfRjOAGNEP9SOn7Mw
l8JoNz1P8PmdknpXj1t8jesr+/NQrfCZ/xBlRhAjE2oh2zgfMw9R6+gLfYRF87ky
dW3y1ghkdpDWbnykVNv/HdjzLDlo1tf3+vYJzkqrxFKvVqhxqg5h0d4fGhIm0RFW
jfW+jARCHyKb
-----END CERTIFICATE-----
'''

PRIVATE_KEY_BODY = '''-----BEGIN PRIVATE KEY-----
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
mdFGLUeaGXZxkZ+NRcUcmJQLmE3SnA==
-----END PRIVATE KEY-----
'''

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

def create_config():
    collection = Collection("inventory")

    config = collection.get_object(CONFIG_OBJUUID)

    config.object = {
        "type" : "config",
        "parent" : SETTINGS_CONTAINER_OBJUUID,
        "concurrency" : 20,
        "brand" : "valarie",
        "banner" : "<h1>Valarie</h1>",
        "title" : "Valarie",
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
            }
        }
    }
    
    config.set()
    
    return config

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

def create_public_key():
    collection = Collection("inventory")
    
    text_file = collection.get_object(PUBLIC_KEY_OBJUUID)
    
    text_file.object = {
        "type" : "text file",
        "parent" : SETTINGS_CONTAINER_OBJUUID,
        "children" : [],
        "name" : "Public Key",
        "body" : PUBLIC_KEY_BODY,
        "language" : "plain_text",
        "icon" : "/images/config_icon.png",
        "context" : {
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit text file",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : text_file.objuuid
                    }
                }
            }
        }
    }
    
    text_file.set()
    
    return text_file

def create_private_key():
    collection = Collection("inventory")
    
    text_file = collection.get_object(PRIVATE_KEY_OBJUUID)
    
    text_file.object = {
        "type" : "text file",
        "parent" : SETTINGS_CONTAINER_OBJUUID,
        "children" : [],
        "name" : "Private Key",
        "body" : PRIVATE_KEY_BODY,
        "language" : "plain_text",
        "icon" : "/images/config_icon.png",
        "context" : {
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit text file",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : text_file.objuuid
                    }
                }
            }
        }
    }
    
    text_file.set()
    
    return text_file

def create_settings_container():
    collection = Collection("inventory")
    
    container = collection.get_object(SETTINGS_CONTAINER_OBJUUID)
    
    container.object = {
        "type" : "container",
        "parent" : "#",
        "children" : [
            TASK_PROTO_OBJUUID,
            CONSOLE_PROTO_OBJUUID,
            PUBLIC_KEY_OBJUUID,
            PRIVATE_KEY_OBJUUID,
            SETTINGS_CONTAINER_OBJUUID
        ],
        "name" : "Settings",
        "icon" : "images/tree_icon.png",
        "context" : {
        }
    }
    
    container.set()
    
    return container
