#!/usr/bin/python3
"""This module implements the inventory routes."""
from typing import Any, Dict, List
from zipfile import ZipFile

import cherrypy
from cherrypy.lib.static import serve_fileobj

from valarie.dao.document import Collection, Object
from valarie.controller import logging
from valarie.controller.container import create_container
from valarie.controller.task import create_task
from valarie.controller.procedure import create_procedure
from valarie.controller.controller import create_controller
from valarie.controller.textfile import create_text_file
from valarie.controller.host import create_host
from valarie.controller.hostgroup import create_host_group
from valarie.controller.console import create_console
from valarie.controller.invfile import load_zip, load_file_from_io
from valarie.controller.statuscode import create_status_code, get_status_objects
from valarie.controller.inventory import (
    get_child_tree_nodes,
    set_parent_objuuid,
    get_context_menu,
    delete_node,
    copy_object,
    import_objects_zip,
    export_objects_zip,
    export_files_zip
)

class Inventory(): # pylint: disable=too-many-public-methods
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
        return {"id": objuuid}

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
        try:
            posted_object = cherrypy.request.json

            logging.info(posted_object['name'])

            inventory = Collection("inventory")
            current = inventory.get_object(posted_object["objuuid"])
            current.object = posted_object
            current.set()
        except Exception as exception:
            logging.error(exception)
            raise exception

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
        try:
            logging.info(f"{len(objuuids.split(','))} objects")
            mem_file = export_objects_zip(objuuids)
            cherrypy.response.headers['Content-Type'] = "application/x-download"
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.objects.zip'
            return serve_fileobj(mem_file.getvalue())
        except Exception as exception:
            logging.error(exception)
            raise exception

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
        try:
            logging.info(f"{len(objuuids.split(','))} objects")
            mem_file = export_files_zip(objuuids)
            cherrypy.response.headers['Content-Type'] = "application/x-download"
            cherrypy.response.headers['Content-Disposition'] = 'attachment; filename=export.files.zip'
            return serve_fileobj(mem_file.getvalue())
        except Exception as exception:
            logging.error(exception)
            raise exception

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
        try:
            logging.info(file.filename)
            import_objects_zip(ZipFile(file.file, 'r'))
            return {}
        except Exception as exception:
            logging.error(exception)
            raise exception

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
        try:
            logging.info(file.filename)
            load_zip(ZipFile(file.file, 'r'))
            return {}
        except Exception as exception:
            logging.error(exception)
            raise exception

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
        try:
            logging.info(file.filename)
            load_file_from_io(file.file, file.filename)
            return {}
        except Exception as exception:
            logging.error(exception)
            raise exception
