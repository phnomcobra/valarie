#!/usr/bin/python

import traceback
import hashlib

from valarie.dao.document import Collection
from valarie.dao.utils import sucky_uuid

from valarie.model.datastore import File, create_binary_file
from valarie.model.textfile import create_text_file
from valarie.model.container import create_container

CHAR_THRESHOLD = 0.3
TEXT_CHARACTERS = ''.join(
    [chr(code) for code in range(32,127)] + list('\b\f\n\r\t')
)

def is_binary(file_data):
    data_length = len(file_data)
        
    if not data_length:
        return False
    
    if '\x00' in file_data:
        return True
    
    binary_length = len(file_data.translate(None, TEXT_CHARACTERS))
    
    return float(binary_length) / data_length >= CHAR_THRESHOLD
                             
def load_zip(archive, root_objuuid = "#"):
    files = {}
    
    for filename in archive.namelist():
        files[filename] = archive.read(filename)
    
    load_files(files, root_objuuid)
        
def load_files(files, root_objuuid = "#"):
    containers = {
        "containers" : {},
        "objuuid" : root_objuuid
    }
        
    directories = []

    for fname, fdata in files.iteritems():
        subdirs = fname.split("/")[:-1]
        dname = "/" + "/".join(subdirs)
                
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
                    "objuuid" : sucky_uuid()
                }
                            
                create_container(parent_objuuid, \
                                 sdname, \
                                 current_container["containers"][sdname]["objuuid"])
                            
            parent_objuuid = current_container["containers"][sdname]["objuuid"]
                        
            current_container = current_container["containers"][sdname]
            
    for fname, fdata in files.iteritems():
        current_container = containers
                    
        sfnames = fname.split("/")
                    
        parent_objuuid = containers["objuuid"]
                
        for i, sfname in enumerate(sfnames):
            if i == len(sfnames) - 1:
                if is_binary(fdata):
                    # binary file inventory object
                    bf = create_binary_file(parent_objuuid, sfname)
                    
                    # data store file
                    df = File(bf.object["sequuid"])
                                
                    sha1hash = hashlib.sha1()
                                
                    df.write(fdata)
                    sha1hash.update(fdata)

                    df.close()

                    bf.object["size"] = df.size()
                    bf.object["sha1sum"] = sha1hash.hexdigest()
                    bf.set()
                else:
                    tf = create_text_file(parent_objuuid, sfname)
                    tf.object["body"] = fdata
                    tf.set()
            else:
                parent_objuuid = current_container["containers"][sfname]["objuuid"]
                        
                current_container = current_container["containers"][sfname]
