#!/usr/bin/python

import traceback
import hashlib

from valarie.controller.messaging import add_message
from valarie.controller.flags import touch_flag

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
                             
class ZipUpload:
    def __init__(self):
        self.containers = {
            "containers" : {},
            "objuuid" : "#"
        }
        
        self.files = {}
        self.directories = []

    def execute(self, archive):
        try:
            for filename in archive.namelist():
                self.files[filename] = archive.read(filename)
            
                subdirs = filename.split("/")[:-1]
                dname = "/" + "/".join(subdirs)
                
                if dname not in self.directories and dname != "/":
                    self.directories.append(dname)
                
            for dname in self.directories:
                current_container = self.containers
                    
                sdnames = dname.split("/")[1:]
                
                parent_objuuid = self.containers["objuuid"]
                    
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
            
            for fname, fdata in self.files.iteritems():
                current_container = self.containers
                    
                sfnames = fname.split("/")
                    
                parent_objuuid = self.containers["objuuid"]
                
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
                                
                            add_message(fname)
                        else:
                            tf = create_text_file(parent_objuuid, sfname)
                            tf.object["body"] = fdata
                            tf.set()
                                
                            add_message(fname)
                    else:
                        parent_objuuid = current_container["containers"][sfname]["objuuid"]
                        
                        current_container = current_container["containers"][sfname]
                        
            touch_flag("inventoryState")
        except:
            add_message(traceback.format_exc())
