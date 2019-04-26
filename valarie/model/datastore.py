#!/usr/bin/python

from valarie.dao.document import Collection

CHUNK_SIZE = 65536

def create_binary_file(parent_objuuid, name = "New Binary File", objuuid = None):
    collection = Collection("inventory")
    
    binary_file = collection.get_object(objuuid)
    
    binary_file.object = {
        "type" : "binary file",
        "parent" : parent_objuuid,
        "children" : [],
        "name" : name,
        "size" : 0,
        "sha1sum" : 0,
        "sequuid" : File()._File__sequence.objuuid,
        "icon" : "/images/binary_file_icon.png",
        "context" : {
            "delete" : {
                "label" : "Delete",
                "action" : {
                    "method" : "delete node",
                    "route" : "inventory/ajax_delete",
                    "params" : {
                        "objuuid" : binary_file.objuuid
                    }
                }
            },
            "edit" : {
                "label" : "Edit",
                "action" : {
                    "method" : "edit binary file",
                    "route" : "inventory/ajax_get_object",
                    "params" : {
                        "objuuid" : binary_file.objuuid
                    }
                }
            }
        }
    }
    
    binary_file.set()
    
    if parent_objuuid != "#":
        parent = collection.get_object(parent_objuuid)
        parent.object["children"] = collection.find_objuuids(parent = parent_objuuid)
        parent.set()
    
    return binary_file

def new_chunk():
    datastore = Collection("datastore")
    
    chunk = datastore.get_object()
    chunk.object = {
        "data" : bytearray(CHUNK_SIZE),
        "type" : "chunk",
    }
    chunk.set()
    
    return chunk

def new_sequence(sequuid = None):
    datastore = Collection("datastore")
    
    sequence = datastore.get_object(sequuid)
    sequence.object = {
        "chunks" : [],
        "size" : 0,
        "type" : "sequence"
    }
    sequence.set()
    
    return sequence

def delete_sequence(sequuid):
    datastore = Collection("datastore")
    
    sequence = datastore.get_object(sequuid)
    
    if "chunks" in sequence.object:
        for chunkid in sequence.object["chunks"]:
            datastore.get_object(chunkid).destroy()
    
    sequence.destroy()

def copy_sequence(sequuid):
    inp_f = File(sequuid)
    out_f = File()
    
    chunk = inp_f.read(CHUNK_SIZE)
    out_f.write(chunk)
    
    while len(chunk) > 0:
        chunk = inp_f.read(CHUNK_SIZE)
        out_f.write(chunk)
    
    out_f.close()
    inp_f.close()
    
    return out_f._File__sequence.objuuid

class File:
    def __init__(self, sequuid = None):
        self.__position = 0L
        self.__chunk_position = 0
        self.__datastore = Collection("datastore")
        self.__chunk = None
        self.__chunk_index = 0
        self.__chunk_changed = False
        self.__end_of_sequence = False
        self.__following_write = False
        
        if sequuid in self.__datastore.find_objuuids(type = "sequence"):
            self.__sequence = self.__datastore.get_object(sequuid)
            self.__chunk = self.__datastore.get_object(self.__sequence.object["chunks"][0])
        else:
            self.__sequence = new_sequence(sequuid)
            self.__chunk = new_chunk()
            self.__sequence.object["chunks"].append(self.__chunk.objuuid)
            self.__sequence.set()
        
    def __del__(self):
        self.close()
    
    def sequuid(self):
        return self.__sequence.object["objuuid"]
    
    def delete(self):
        delete_sequence(self.__sequence.object["objuuid"])
    
    def tell(self):
        return self.__position
    
    def size(self):
        return self.__sequence.object["size"]
    
    def close(self):
        self.__sequence.set()
        self.__chunk.set()
    
    def open(self, **kargs):
        self.__init__(kargs)
    
    def seek(self, seek_position):
        if seek_position < 0 or seek_position >= self.__sequence.object["size"]:
            raise IndexError("Position out of bounds!")
        
        i = int(seek_position / CHUNK_SIZE)
        if self.__chunk_index != i:
            if self.__chunk_changed == True:
                self.__chunk.set()
                
            self.__chunk = self.__datastore.get_object(self.__sequence.object["chunks"][i])
            self.__chunk_index = i
            
            self.__chunk_changed = False
            
        self.__chunk_position = seek_position % CHUNK_SIZE
        
        self.__position = seek_position
        
        self.__following_write = False
        
        self.__end_of_sequence = False
    
    def read(self, num_bytes = None):
        buffer = bytearray()
        
        if self.__end_of_sequence == True:
            pass
        elif num_bytes == None:
            for i in range(self.__position, self.__sequence.object["size"]):
                buffer.append(self.__chunk.object["data"][self.__chunk_position])
                
                try:
                    self.seek(1 + self.__position)
                except IndexError:
                    self.__end_of_sequence = True
                    break
        else:
            for i in range(self.__position, self.__position + num_bytes):
                buffer.append(self.__chunk.object["data"][self.__chunk_position])
                
                try:
                    self.seek(1 + self.__position)
                except IndexError:
                    self.__end_of_sequence = True
                    break
        
        return buffer

    def truncate(self, num_bytes = None):
        if num_bytes == None:
            self.resize(self.__position + 1)
        else:
            self.resize(num_bytes)
    
    def resize(self, num_bytes):
        self.__sequence.object["size"] = num_bytes
        
        num_chunks = int(num_bytes / CHUNK_SIZE) + 1
        num_chunks_exist = len(self.__sequence.object["chunks"])
        
        if num_chunks_exist < num_chunks:
            for i in range(num_chunks_exist, num_chunks):
                chunk = new_chunk()
                self.__sequence.object["chunks"].append(chunk.objuuid)
        else:
            for i in range(num_chunks_exist - 1, num_chunks - 1, -1):
                self.__datastore.get_object(self.__sequence.object["chunks"][i]).destroy()
                self.__sequence.object["chunks"].pop()
    
    def write(self, raw_buffer):
        buffer = bytearray()
        
        buffer.extend(raw_buffer)
        
        if self.__following_write == True and \
           len(buffer) > 0 and \
           self.size() < self.__position + len(buffer) + 1:
            self.resize(self.__position + len(buffer) + 1)
            self.seek(1 + self.__position)
        elif self.__following_write == False and \
             len(buffer) > 0 and \
             self.size() < self.__position + len(buffer):
            self.resize(self.__position + len(buffer))
        
        for i in range(0, len(buffer)):
            self.__chunk.object["data"][self.__chunk_position] = buffer[i]
            self.__chunk_changed = True
            
            if i < len(buffer) - 1:
                self.seek(1 + self.__position)
        
        self.__following_write = True

collection = Collection("datastore")
collection.create_attribute("type", "['type']")