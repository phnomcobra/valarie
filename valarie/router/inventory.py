#!/usr/bin/python3
"""This module implements the inventory routes."""

import cherrypy
import json
import zipfile
import io
import hashlib
from typing import Any, Dict, List

from cherrypy.lib.static import serve_fileobj

from valarie.controller.messaging import add_message

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
    """This class registers the inventory endpoint methods as endpoints."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_child_tree_nodes(cls, objuuid: str) -> List[Dict]:
        """This function registers the endpoint that retrieves a list of jstree
        child nodes beginning at the specified UUID in the inventory.

        Args:
            objuuid:
                The UUID to discover nodes from.

        Returns:
            JSON string of list of jstree nodes.
        """
        return get_child_tree_nodes(objuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def move_object(cls, objuuid: str, parent_objuuid: str) -> Dict:
        """This function moves an object to a new location in the invnentory by
        changing which object is its parent.

        Args:
            objuuid:
                The UUID of the object to move.

            parent_object:
                The UUID of the object's new parent.
        """
        set_parent_objuuid(objuuid, parent_objuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def copy_object(cls, objuuid: str) -> Object:
        """This function registers the endpoint that copies an object and its
        children in the inventory.

        Args:
            objuuid:
                The UUID of the object to copy.

        Returns:
            JSON string of the newly created inventory object.
        """
        return copy_object(objuuid).object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_container(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a container
        object in the inventory.

        Args:
            objuuid:
                The UUID of the container's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_container(objuuid, "New Container").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_host(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a host
        object in the inventory.

        Args:
            objuuid:
                The UUID of the host's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_host(objuuid, "New Host").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_text_file(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a text file
        object in the inventory.

        Args:
            objuuid:
                The UUID of the text file's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_text_file(objuuid, "New Text File.txt").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_host_group(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a host group
        object in the inventory.

        Args:
            objuuid:
                The UUID of the host groups's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_host_group(objuuid, "New Host Group").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_console(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a console
        object in the inventory.

        Args:
            objuuid:
                The UUID of the console's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_console(objuuid, "New Console").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_task(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a task
        object in the inventory.

        Args:
            objuuid:
                The UUID of the task's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_task(objuuid, "New Task").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_status_code(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a status
        code object in the inventory.

        Args:
            objuuid:
                The UUID of the status code's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_status_code(objuuid, "New Status Code").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_procedure(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a procedure
        object in the inventory.

        Args:
            objuuid:
                The UUID of the procedure's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_procedure(objuuid, "New Procedure").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def create_controller(cls, objuuid: str) -> Object:
        """This function registers the endpoint that creates a controller
        object in the inventory.

        Args:
            objuuid:
                The UUID of the controller's parent object.

        Returns:
            JSON string of the newly created inventory object.
        """
        return create_controller(objuuid, "New Controller").object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def delete(cls, objuuid: str) -> Dict:
        """This function registers the endpoint that deletes an object and
        its children in the inventory.

        Args:
            objuuid:
                The UUID of the object to delete.

        Returns:
            JSON string of the id just deleted.
        """
        delete_node(objuuid)
        return { "id": objuuid }

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def context(cls, objuuid: str) -> List[Dict]:
        """This function registers the endpoint that retrieves an inventory
        objects context menu list.

        Args:
            objuuid:
                The UUID of the inventory object.

        Returns:
            JSON string of a list of context menu items.
        """
        return get_context_menu(objuuid)

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_object(cls, objuuid: str) -> Object:
        """This function registers the endpoint that retrieves an inventory
        object.

        Args:
            objuuid:
                The UUID of the inventory object.

        Returns:
            JSON string of the inventory object.
        """
        return Collection("inventory").get_object(objuuid).object

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_status_objects(cls) -> List:
        """This function registers the endpoint that retrieves a
        list of status objects that are present in the inventory.

        Returns:
            JSON string of the status code objects.
        """
        return get_status_objects()

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def post_object(cls) -> Object:
        """This function registers the endpoint that posts an inventory
        object. An inventory object is either created or updated with the
        object that is posted.

        Returns:
            JSON string of the inventory object.
        """
        object = cherrypy.request.json

        inventory = Collection("inventory")
        current = inventory.get_object(object["objuuid"])
        current.object = object
        current.set()

        return current.object

    @classmethod
    @cherrypy.expose
    def export_objects_zip(cls, objuuids: str) -> Any:
        """This function registers the endpoint that exports inventory objects to
        a ZIP archive.

        Args:
            objuuids:
                A comma delivered list of UUIDs of the inventory objects to export.

        Returns:
            A static file response.
        """
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
        """This function registers the endpoint that exports certain inventory
        objects to a ZIP archive. This mode of export deals exclusively with text files,
        binary files, and result objects.

        Args:
            objuuids:
                A comma delivered list of UUIDs of the inventory objects to export.

        Returns:
            A static file response.
        """
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
        """This function registers the endpoint that imports inventory
        objects from a ZIP archive.

        Args:
            file:
                A file handle.
        """
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
        """This function registers the endpoint that imports text and
        binary files from a ZIP archive into the inventory.

        Args:
            file:
                A file handle.
        """
        add_message("inventory controller: importing inventory files...")
        load_zip(zipfile.ZipFile(file.file, 'r'))
        add_message("INVENTORY IMPORT COMPLETE")
        return {}

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def import_file(cls, file: Any) -> Dict:
        """This function registers the endpoint that imports an individual text
        or binary file into the inventory.

        Args:
            file:
                A file handle.
        """
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
