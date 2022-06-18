#!/usr/bin/python3

import cherrypy
import json
import traceback
import zipfile
import io
import hashlib

from cherrypy.lib.static import serve_fileobj
from time import sleep

from valarie.router.messaging import add_message

from valarie.dao.document import Collection

from valarie.dao.datastore import File as DatastoreFile
from valarie.controller.container import create_container
from valarie.controller.task import create_task
from valarie.controller.procedure import create_procedure
from valarie.controller.controller import create_controller
from valarie.controller.textfile import create_text_file
from valarie.dao.datastore import create_binary_file
from valarie.controller.host import create_host
from valarie.controller.hostgroup import create_host_group
from valarie.controller.console import create_console
from valarie.controller.invfile import load_zip, is_binary
from valarie.controller.statuscode import create_status_code, get_status_objects
from valarie.controller.inventory import (
    get_child_tree_nodes,
    set_parent_objuuid,
    get_context_menu,
    delete_node,
    copy_object,
    import_objects,
    get_fq_name
)

class Inventory():
    def __init__(self):
        self.moving = False

    @classmethod
    @cherrypy.expose
    def get_child_tree_nodes(cls, objuuid: str) -> str:
        return json.dumps(get_child_tree_nodes(objuuid))

    @cherrypy.expose
    def move_object(self, objuuid: str, parent_objuuid: str):
        while self.moving:
            sleep(.1)

        try:
            self.moving = True
            set_parent_objuuid(objuuid, parent_objuuid)
            return json.dumps({})
        finally:
            self.moving = False

    @cherrypy.expose
    def copy_object(self, objuuid: str) -> str:
        while self.moving:
            sleep(.1)

        return json.dumps(copy_object(objuuid).object)

    @cherrypy.expose
    def create_container(self, objuuid):
        try:
            container = create_container(objuuid, "New Container")

            return json.dumps(container.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def create_host(self, objuuid):
        try:
            host = create_host(objuuid, "New Host")

            return json.dumps(host.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def create_text_file(self, objuuid):
        try:
            text_file = create_text_file(objuuid, "New Text File.txt")

            return json.dumps(text_file.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def create_host_group(self, objuuid):
        try:
            group = create_host_group(objuuid, "New Host Group")

            return json.dumps(group.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def create_console(self, objuuid):
        try:
            console = create_console(objuuid, "New Console")

            return json.dumps(console.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def create_task(self, objuuid):
        try:
            task = create_task(objuuid, "New Task")

            return json.dumps(task.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def create_status_code(self, objuuid):
        try:
            status_code = create_status_code(objuuid, "New Status Code")

            return json.dumps(status_code.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def create_procedure(self, objuuid):
        try:
            procedure = create_procedure(objuuid, "New Procedure")

            return json.dumps(procedure.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def create_controller(self, objuuid):
        try:
            controller = create_controller(objuuid, "New Controller")

            return json.dumps(controller.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def delete(self, objuuid):
        try:
            while self.moving:
                sleep(.1)

            delete_node(objuuid)
            return json.dumps({"id" : objuuid})
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def context(self, objuuid):
        try:
            return json.dumps(get_context_menu(objuuid))
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def get_object(self, objuuid):
        try:
            return json.dumps(Collection("inventory").get_object(objuuid).object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def get_status_objects(self):
        try:
            return json.dumps(get_status_objects())
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def post_object(self):
        try:
            cl = cherrypy.request.headers['Content-Length']
            object = json.loads(cherrypy.request.body.read(int(cl)))

            collection = Collection("inventory")
            current = collection.get_object(object["objuuid"])
            current.object = object
            current.set()

            return json.dumps(current.object)
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def export_objects_zip(self, objuuids):
        add_message("inventory controller: exporting inventory objects...")

        try:
            collection = Collection("inventory")

            inventory = {}

            dstuuids = []

            for objuuid in objuuids.split(","):
                current = collection.get_object(objuuid)

                if current.object["type"] in ["result link"]:
                    continue

                inventory[objuuid] = current.object

                if current.object["type"] == "binary file":
                    dstuuids.append(current.object["sequuid"])

                add_message("inventory controller: exported: {0}, type: {1}, name: {2}".format(objuuid, current.object["type"], current.object["name"]))

            cherrypy.response.headers['Content-Type'] = "application/x-download"
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.objects.zip'

            mem_file = io.BytesIO()

            with zipfile.ZipFile(mem_file, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
                zf.writestr('inventory.json', json.dumps(inventory, indent = 4, sort_keys = True))

                for dstuuid in dstuuids:
                    zf.writestr('{0}.bin'.format(dstuuid), DatastoreFile(dstuuid).read())

            add_message("INVENTORY EXPORT COMPLETE")

            return serve_fileobj(mem_file.getvalue())
        except:
            add_message(traceback.format_exc())

    @cherrypy.expose
    def export_files_zip(self, objuuids):
        add_message("inventory controller: exporting inventory files...")

        try:
            collection = Collection("inventory")

            mem_file = io.BytesIO()

            with zipfile.ZipFile(mem_file, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
                for objuuid in objuuids.split(","):
                    current = collection.get_object(objuuid)

                    if current.object["type"] in ["result link"]:
                        continue

                    # zip archive can't take a leading slash
                    filename = get_fq_name(objuuid)[1:]
                    add_message(filename)

                    if current.object["type"] == "binary file":
                        add_message("inventory controller: exported: " + filename)
                        zf.writestr(filename, DatastoreFile(current.object["sequuid"]).read())

                    elif current.object["type"] == "text file":
                        add_message("inventory controller: exported: " + filename)
                        zf.writestr(filename, current.object["body"].encode())


            cherrypy.response.headers['Content-Type'] = "application/x-download"
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.files.zip'

            add_message("INVENTORY EXPORT COMPLETE")

            return serve_fileobj(mem_file.getvalue())
        except:
            add_message(traceback.format_exc())


    @cherrypy.expose
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

                    datastore_file.close()

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
    def import_files_zip(self, file):
        add_message("inventory controller: importing inventory files...")

        try:
            load_zip(zipfile.ZipFile(file.file, 'r'))
        except:
            add_message(traceback.format_exc())

        add_message("INVENTORY IMPORT COMPLETE")

        return json.dumps({})

    @cherrypy.expose
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
                text_file.object["body"] = fdata.decode()
                text_file.set()
        except:
            add_message(traceback.format_exc())

        add_message("INVENTORY IMPORT COMPLETE")

        return json.dumps({})
