#!/usr/bin/python3

import cherrypy
import json
import zipfile
import io
import hashlib
from typing import Any, Dict, List

from cherrypy.lib.static import serve_fileobj
from time import sleep

from valarie.router.messaging import add_message

from valarie.dao.document import Collection, Object
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
    @cherrypy.tools.json_out()
    def get_child_tree_nodes(cls, objuuid: str) -> List[Dict]:
        return get_child_tree_nodes(objuuid)

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def move_object(self, objuuid: str, parent_objuuid: str) -> Dict:
        while self.moving:
            sleep(.1)

        try:
            self.moving = True
            set_parent_objuuid(objuuid, parent_objuuid)
            return {}
        finally:
            self.moving = False

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def copy_object(self, objuuid: str) -> Object:
        while self.moving:
            sleep(.1)

        return copy_object(objuuid).object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_container(cls, objuuid: str) -> Object:
        return create_container(objuuid, "New Container").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_host(cls, objuuid: str) -> Object:
        return create_host(objuuid, "New Host").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_text_file(cls, objuuid: str) -> Object:
        return create_text_file(objuuid, "New Text File.txt").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_host_group(cls, objuuid: str) -> Object:
        return create_host_group(objuuid, "New Host Group").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_console(cls, objuuid: str) -> Object:
        return create_console(objuuid, "New Console").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_task(cls, objuuid: str) -> Object:
        return create_task(objuuid, "New Task").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_status_code(cls, objuuid: str) -> Object:
        return create_status_code(objuuid, "New Status Code").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_procedure(cls, objuuid: str) -> Object:
        return create_procedure(objuuid, "New Procedure").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_controller(cls, objuuid: str) -> Object:
        return create_controller(objuuid, "New Controller").object

    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delete(self, objuuid: str) -> Dict:
        while self.moving:
            sleep(.1)
        delete_node(objuuid)
        return { "id": objuuid }

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def context(cls, objuuid: str) -> List[Dict]:
        return get_context_menu(objuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_object(cls, objuuid: str) -> Object:
        return Collection("inventory").get_object(objuuid).object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_status_objects(cls) -> List:
        return get_status_objects()

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def post_object(cls) -> Object:
        cl = cherrypy.request.headers['Content-Length']
        object = json.loads(cherrypy.request.body.read(int(cl)))

        inventory = Collection("inventory")
        current = inventory.get_object(object["objuuid"])
        current.object = object
        current.set()

        return current.object

    @classmethod
    @cherrypy.expose
    def export_objects_zip(cls, objuuids: str) -> Any:
        add_message("inventory controller: exporting inventory objects...")

        inventory = Collection("inventory")

        output = {}

        dstuuids = []

        for objuuid in objuuids.split(","):
            current = inventory.get_object(objuuid)

            if current.object["type"] in ["result link"]:
                continue

            output[objuuid] = current.object

            if current.object["type"] == "binary file":
                dstuuids.append(current.object["sequuid"])

            add_message(f"inventory controller: exported: {objuuid}, type: {current.object['type']}, name: {current.object['name']}")

        cherrypy.response.headers['Content-Type'] = "application/x-download"
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.objects.zip'

        mem_file = io.BytesIO()

        with zipfile.ZipFile(mem_file, mode = 'w', compression = zipfile.ZIP_DEFLATED) as zf:
            zf.writestr('inventory.json', json.dumps(output, indent=4, sort_keys=True))

            for dstuuid in dstuuids:
                zf.writestr('{0}.bin'.format(dstuuid), DatastoreFile(dstuuid).read())

        add_message("INVENTORY EXPORT COMPLETE")

        return serve_fileobj(mem_file.getvalue())

    @classmethod
    @cherrypy.expose
    def export_files_zip(cls, objuuids: str) -> Any:
        add_message("inventory controller: exporting inventory files...")

        inventory = Collection("inventory")
        results = Collection("results")

        mem_file = io.BytesIO()

        with zipfile.ZipFile(mem_file, mode='w', compression=zipfile.ZIP_DEFLATED) as zf:
            for objuuid in objuuids.split(","):
                current = inventory.get_object(objuuid)

                # zip archive can't take a leading slash or names containing colons
                filename = get_fq_name(objuuid)[1:].replace(':', '')
                add_message(filename)

                if current.object["type"] == "binary file":
                    add_message("inventory controller: exported: " + filename)
                    zf.writestr(filename, DatastoreFile(current.object["sequuid"]).read())
                elif current.object["type"] == "text file":
                    add_message("inventory controller: exported: " + filename)
                    zf.writestr(filename, current.object["body"].encode())
                elif current.object["type"] == "result link":
                    add_message("inventory controller: exported: " + filename)
                    result = results.get_object(current.object['resuuid'])
                    zf.writestr(f'{filename}.json', json.dumps(result.object, indent=4).encode())

        cherrypy.response.headers['Content-Type'] = "application/x-download"
        cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.files.zip'

        add_message("INVENTORY EXPORT COMPLETE")

        return serve_fileobj(mem_file.getvalue())


    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def import_objects_zip(cls, file: Any) -> Dict:
        add_message("inventory controller: importing inventory objects...")

        archive = zipfile.ZipFile(file.file, 'r')

        objects = json.loads(archive.read("inventory.json"))

        for _id, object in objects.items():
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

        add_message("INVENTORY IMPORT COMPLETE")

        return {}

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def import_files_zip(cls, file: Any) -> Dict:
        add_message("inventory controller: importing inventory files...")
        load_zip(zipfile.ZipFile(file.file, 'r'))
        add_message("INVENTORY IMPORT COMPLETE")
        return {}

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def import_file(cls, file: Any) -> Dict:
        add_message("inventory controller: importing inventory file...")

        fdata = file.file.read()

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

        add_message("INVENTORY IMPORT COMPLETE")

        return {}
