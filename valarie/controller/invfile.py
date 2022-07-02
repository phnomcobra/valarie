#!/usr/bin/python3
"""This module implements functions for storing files and managing files and
links in the inventory and datastore."""
import hashlib
from typing import Dict
from zipfile import ZipFile

from valarie.dao.utils import get_uuid_str
from valarie.dao.datastore import File, create_binary_file
from valarie.controller.textfile import create_text_file
from valarie.controller.container import create_container

CHAR_THRESHOLD = 0.3
TEXT_CHARACTERS = ''.join(
    [chr(code) for code in range(32, 127)] + list('\b\f\n\r\t')
).encode()

def is_binary(file_data: bytes) -> bool:
    """This function analyzes a byte array and determines if it's a binary
    file or not.

    Args:
        file_data:
            bytes

    Returns:
        True if the file data is from a binary file."""
    data_length = len(file_data)

    if not data_length:
        return False

    if b'\x00' in file_data:
        return True

    binary_length = len(file_data.translate(None, TEXT_CHARACTERS))

    return float(binary_length) / data_length >= CHAR_THRESHOLD

def load_zip(archive: ZipFile, root_objuuid: str = "#"):
    """This function reads all the files in and archive and places
    the byte arrays into a dictionary that is keyed with their archive
    names.

    Args:
        archive:
            The ZipFile object being read.

        root_objuuid:
            The UUID of the inventory object that will be the parent
            for any files or containers that may be created during the
            load.
    """
    files = {}

    for filename in archive.namelist():
        files[filename] = archive.read(filename)

    load_files(files, root_objuuid)

# pylint: disable=too-many-locals
def load_files(files: Dict[str, bytes], root_objuuid: str = "#"):
    """This function reads a dictionary of byte arrays and loads them
    into the inventory and datastore. Archive names are tokenized and
    used to create a directory tree under the parent inventory object.
    Sub directories are translated to container objects. Byte arrays
    translate to either text file objects or a combination of datastore
    sequences and binary file objects.

    Args:
        files:
            Dictionary of byte arrays keyed with their archive names.

        root_objuuid:
            The UUID of the inventory object that will be the parent
            for any files or containers that may be created during the
            load.
    """
    containers = {
        "containers" : {},
        "objuuid" : root_objuuid
    }

    directories = []

    for fname, fdata in files.items():
        subdirs = fname.split("/")[:-1]
        dname = f'/{"/".join(subdirs)}'

        if dname not in directories and dname != "/":
            directories.append(dname)

    for dname in directories:
        current_container = containers

        sdnames = dname.split("/")[1:]

        parent_objuuid = containers["objuuid"]

        for sdname in sdnames:
            if sdname not in current_container["containers"]:
                current_container["containers"][sdname] = {
                    "containers" : {},
                    "objuuid" : get_uuid_str()
                }

                create_container(
                    parent_objuuid,
                    sdname,
                    current_container["containers"][sdname]["objuuid"]
                )

            parent_objuuid = current_container["containers"][sdname]["objuuid"]

            current_container = current_container["containers"][sdname]

    for fname, fdata in files.items():
        current_container = containers

        sfnames = fname.split("/")

        parent_objuuid = containers["objuuid"]

        for i, sfname in enumerate(sfnames):
            if i == len(sfnames) - 1:
                if is_binary(fdata):
                    binary_file = create_binary_file(parent_objuuid, sfname)

                    datastore_file = File(binary_file.object["sequuid"])

                    sha1hash = hashlib.sha1()

                    datastore_file.write(fdata)
                    sha1hash.update(fdata)

                    datastore_file.close()

                    binary_file.object["size"] = datastore_file.size()
                    binary_file.object["sha1sum"] = sha1hash.hexdigest()
                    binary_file.set()
                else:
                    text_file = create_text_file(parent_objuuid, sfname)
                    text_file.object["body"] = fdata.decode()
                    text_file.set()
            else:
                parent_objuuid = current_container["containers"][sfname]["objuuid"]

                current_container = current_container["containers"][sfname]
