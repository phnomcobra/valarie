#!/usr/bin/python

import cherrypy
import json
import traceback
import zipfile
import io
import hashlib

from cherrypy.lib.static import serve_fileobj
from time import sleep

from valarie.controller.messaging import add_message
from valarie.controller.auth import require

from valarie.dao.document import Collection

from valarie.model.datastore import File as DatastoreFile
from valarie.model.container import create_container
from valarie.model.task import create_task
from valarie.model.procedure import create_procedure
from valarie.model.controller import create_controller
from valarie.model.textfile import create_text_file
from valarie.model.datastore import create_binary_file
from valarie.model.host import create_host
from valarie.model.hostgroup import create_host_group
from valarie.model.console import create_console
from valarie.model.invfile import load_zip, \
                                  is_binary
from valarie.model.statuscode import create_status_code, \
                                     get_status_objects
from valarie.model.inventory import get_child_nodes, \
                                    set_parent_objuuid, \
                                    get_context_menu, \
                                    delete_node, \
                                    copy_object, \
                                    import_objects, \
                                    get_fq_name

class Inventory(object):
    def __init__(self):
        self.moving = False

    @cherrypy.expose
    @require()
    def ajax_roots(self, objuuid):
        add_message("inventory controller: load inventory: {0}".format(objuuid))
        try:
            return json.dumps(get_child_nodes(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_move(self, objuuid, parent_objuuid):
        add_message("inventory controller: move inventory object: {0}".format(objuuid))
        while self.moving:
            sleep(.1)
        
        try:
            self.moving = True
            set_parent_objuuid(objuuid, parent_objuuid)
        except:
            add_message(traceback.format_exc())
        finally:
            self.moving = False

        return json.dumps({})
    
    @cherrypy.expose
    @require()
    def ajax_copy_object(self, objuuid):
        add_message("inventory controller: copy: {0}".format(objuuid))

        try:
            while self.moving:
                sleep(.1)
            
            return json.dumps(copy_object(objuuid).object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    @require()
    def ajax_create_container(self, objuuid):
        add_message("inventory controller: create container: {0}".format(objuuid))
        try:
            container = create_container(objuuid, "New Container")
            
            return json.dumps(container.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_host(self, objuuid):
        add_message("inventory controller: create host: {0}".format(objuuid))
        try:
            host = create_host(objuuid, "New Host")
            
            return json.dumps(host.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_text_file(self, objuuid):
        add_message("inventory controller: create text_file: {0}".format(objuuid))
        try:
            text_file = create_text_file(objuuid, "New Text File.txt")
            
            return json.dumps(text_file.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_host_group(self, objuuid):
        add_message("inventory controller: create host group: {0}".format(objuuid))
        try:
            group = create_host_group(objuuid, "New Host Group")
            
            return json.dumps(group.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_console(self, objuuid):
        add_message("inventory controller: create console: {0}".format(objuuid))
        try:
            console = create_console(objuuid, "New Console")
            
            return json.dumps(console.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_task(self, objuuid):
        add_message("inventory controller: create task: {0}".format(objuuid))
        try:
            current_user = Collection("users").find(sessionid = cherrypy.session.id)[0]
            
            task = create_task(objuuid, \
                               "New Task", \
                               author = "{0} {1}".format(current_user.object["first name"], \
                                                         current_user.object["last name"]), \
                               email = current_user.object["email"], \
                               phone = current_user.object["phone"])
            
            return json.dumps(task.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_status_code(self, objuuid):
        add_message("inventory controller: create status code: {0}".format(objuuid))
        try:
            status_code = create_status_code(objuuid, "New Status Code")
            
            return json.dumps(status_code.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_procedure(self, objuuid):
        add_message("inventory controller: create procedure: {0}".format(objuuid))
        try:
            procedure = create_procedure(objuuid, "New Procedure")
        
            return json.dumps(procedure.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_create_controller(self, objuuid):
        add_message("inventory controller: create controller: {0}".format(objuuid))
        try:
            controller = create_controller(objuuid, "New Controller")
            
            return json.dumps(controller.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_delete(self, objuuid):
        add_message("inventory controller: delete inventory object: {0}".format(objuuid))
        try:
            while self.moving:
                sleep(.1)
            
            delete_node(objuuid)
            return json.dumps({"id" : objuuid})
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_context(self, objuuid):
        add_message("inventory controller: get context menu: {0}".format(objuuid))
        try:
            return json.dumps(get_context_menu(objuuid))
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_object(self, objuuid):
        add_message("inventory controller: get inventory object...")
        try:
            collection = Collection("inventory")
            object = collection.get_object(objuuid).object
            add_message("inventory controller: get: {0}, type: {1}, name: {2}".format(objuuid, object["type"], object["name"]))
            return json.dumps(object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_get_status_objects(self):
        add_message("inventory controller: get status objects...")
        try:
            return json.dumps(get_status_objects())
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def ajax_post_object(self):
        add_message("inventory controller: post inventory object...")
        
        try:
            cl = cherrypy.request.headers['Content-Length']
            object = json.loads(cherrypy.request.body.read(int(cl)))
        
            collection = Collection("inventory")
            current = collection.get_object(object["objuuid"])
            current.object = object
            current.set()
            
            add_message("inventory controller: set: {0}, type: {1}, name: {2}".format(object["objuuid"], object["type"], object["name"]))
        
            return json.dumps(current.object)
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def export_objects_zip(self, objuuids):
        add_message("inventory controller: exporting inventory objects...")
        
        try:
            collection = Collection("inventory")
        
            inventory = {}
            
            dstuuids = []
            
            for objuuid in objuuids.split(","):
                current = collection.get_object(objuuid)
                inventory[objuuid] = current.object
                
                if current.object["type"] == "binary file":
                    dstuuids.append(current.object["sequuid"])
                
                add_message("inventory controller: exported: {0}, type: {1}, name: {2}".format(objuuid, current.object["type"], current.object["name"]))
                
            cherrypy.response.headers['Content-Type'] = "application/x-download"
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.objects.zip'
            
            mem_file = io.StringIO()
            
            with zipfile.ZipFile(mem_file, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('inventory.json', json.dumps(inventory, indent = 4, sort_keys = True))
                
                for dstuuid in dstuuids:
                    zf.writestr('{0}.bin'.format(dstuuid), buffer(DatastoreFile(dstuuid).read()))
            
            add_message("INVENTORY EXPORT COMPLETE")
            
            return serve_fileobj(mem_file.getvalue())
        except:
            add_message(traceback.format_exc())
    
    @cherrypy.expose
    @require()
    def export_files_zip(self, objuuids):
        add_message("inventory controller: exporting inventory files...")
        
        try:
            collection = Collection("inventory")
        
            mem_file = io.StringIO()
            
            with zipfile.ZipFile(mem_file, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
                for objuuid in objuuids.split(","):
                    current = collection.get_object(objuuid)
                    
                    # zip archive can't take a leading slash
                    filename = get_fq_name(objuuid)[1:]
                    
                    if current.object["type"] == "binary file":
                        add_message("inventory controller: exported: " + filename)
                        zf.writestr(filename, buffer(DatastoreFile(current.object["sequuid"]).read()))
                    
                    elif current.object["type"] == "text file":
                        add_message("inventory controller: exported: " + filename)
                        zf.writestr(filename, current.object["body"])


            cherrypy.response.headers['Content-Type'] = "application/x-download"
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.files.zip'
            
            add_message("INVENTORY EXPORT COMPLETE")
            
            return serve_fileobj(mem_file.getvalue())
        except:
            add_message(traceback.format_exc())
    
    
    @cherrypy.expose
    @require()
    def import_objects_zip(self, file):
        add_message("inventory controller: importing inventory objects...")
        
        try:
            archive = zipfile.ZipFile(file.file, 'r')
            
            objects = json.loads(archive.read("inventory.json"))
            
            for objuuid, object in objects.items():
                if object["type"] == "binary file":
                    datastore_file = DatastoreFile(object["sequuid"])
                    
                    zipped_file = archive.open("{0}.bin".format(object["sequuid"]), "r")
                    
                    sha1hash = hashlib.sha1()
                    
                    for chunk in iter(lambda: zipped_file.read(65536), b''):
                        datastore_file.write(chunk)
                        sha1hash.update(chunk)
                    
                    datastore_file.truncate()
                    
                    object["size"] = datastore_file.size()
                    object["sha1sum"] = sha1hash.hexdigest()
            
            import_objects(objects)
            
            objuuids = []
            for objuuid in objects:
                objuuids.append(objuuid)
        except:
            add_message(traceback.format_exc())
        
        add_message("INVENTORY IMPORT COMPLETE")
        
        return json.dumps({})
    
    @cherrypy.expose
    @require()
    def import_files_zip(self, file):
        add_message("inventory controller: importing inventory files...")
        
        try:
            load_zip(zipfile.ZipFile(file.file, 'r'))
        except:
            add_message(traceback.format_exc())
        
        add_message("INVENTORY IMPORT COMPLETE")
        
        return json.dumps({})
    
    @cherrypy.expose
    @require()
    def import_file(self, file):
        add_message("inventory controller: importing inventory file...")
        
        fdata = file.file.read()
        
        try:
            if is_binary(fdata):
                binary_file_inv = create_binary_file("#", file.filename)
            
                binary_file_dst = DatastoreFile(binary_file_inv.object["sequuid"])
            
                sha1hash = hashlib.sha1()
            
                binary_file_dst.write(fdata)
                sha1hash.update(fdata)
            
                binary_file_inv.object["size"] = binary_file_dst.size()
                binary_file_inv.object["sha1sum"] = sha1hash.hexdigest()
                binary_file_inv.set()
            else:
                text_file = create_text_file("#", file.filename)
                text_file.object["body"] = fdata
                text_file.set()
        except:
            add_message(traceback.format_exc())
        
        add_message("INVENTORY IMPORT COMPLETE")
        
        return json.dumps({})
