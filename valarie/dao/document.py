#!/usr/bin/python3
"""This module implements the Document, Collection, and Object classes.
The document class wraps and abstracts the database and the various SQL
driving functions. It serves as the base class with is inherited by the
Collection and Object classes."""
import sqlite3
import pickle
from typing import Dict

from valarie.dao.utils import get_uuid_str

DEFAULT_CONNECTION_STR = "default.sqlite"

class Document:
    """This class wraps and abstracts that database and the SQL driving
    functions. The class manages objects, collections, and collection
    attributes. Additonally, there is functionality for searching and
    enumerating collections."""
    def __init__(self, connection_str: str = DEFAULT_CONNECTION_STR):
        """This function instantiates a document object and initiallizes
        the database if it hasn't been initialized yet.

        Args:
            connection_str:
                A Sqlite connection string."""
        self.connection_str = connection_str
        self.connection = sqlite3.connect(self.connection_str, 300)
        self.connection.text_factory = str

        self.cursor = self.connection.cursor()

        self.cursor.execute("PRAGMA foreign_keys = ON")
        self.connection.commit()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TBL_JSON_COL (
                               COLUUID VARCHAR(36),
                               NAME VARCHAR(64) UNIQUE NOT NULL,
                               PRIMARY KEY (COLUUID));''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TBL_JSON_OBJ (
                               OBJUUID VARCHAR(36),
                               COLUUID VARCHAR(36),
                               VALUE BLOB NOT NULL,
                               PRIMARY KEY (OBJUUID),
                               FOREIGN KEY (COLUUID) REFERENCES TBL_JSON_COL(COLUUID) ON DELETE CASCADE);''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TBL_JSON_ATTR (
                               COLUUID VARCHAR(36),
                               ATTRIBUTE VARCHAR(64),
                               PATH VARCHAR(64),
                               PRIMARY KEY (COLUUID, ATTRIBUTE),
                               FOREIGN KEY (COLUUID) REFERENCES TBL_JSON_COL(COLUUID) ON DELETE CASCADE);''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TBL_JSON_IDX (
                               OBJUUID VARCHAR(36),
                               COLUUID VARCHAR(36),
                               ATTRIBUTE VARCHAR(64),
                               VALUE VARCHAR(64),
                               PRIMARY KEY (OBJUUID, ATTRIBUTE),
                               FOREIGN KEY (OBJUUID) REFERENCES TBL_JSON_OBJ(OBJUUID) ON DELETE CASCADE,
                               FOREIGN KEY (COLUUID, ATTRIBUTE) REFERENCES TBL_JSON_ATTR(COLUUID, ATTRIBUTE) ON DELETE CASCADE);''')

        self.connection.commit()

    def vacuum(self):
        """This function compacts the database."""
        self.cursor.execute("VACUUM;")
        self.connection.commit()

    def create_object(self, coluuid: str, objuuid: str):
        """This function creates a new object in a collection.
        With the exception of setting the object and collection
        UUIDs, the object is empty.

        Args:
            coluuid:
                The collection UUID.

            objuuid:
                The object UUID.
        """
        self.cursor.execute(
            "insert into TBL_JSON_OBJ (COLUUID, OBJUUID, VALUE) values (?, ?, ?);",
            (coluuid, objuuid, pickle.dumps({"objuuid": objuuid, "coluuid": coluuid}))
        )

    def set_object(self, coluuid: str, objuuid: str, object: Dict):
        """This function updates an object in a collection. The object dictionary,
        object UUID, and collection UUID are updated. In addition, previously indexed
        attributes are deleted and reset based on the updated object.

        Args:
            coluuid:
                The collection UUID.

            objuuid:
                The object UUID.

            object:
                The object dictionary that will be stored.
        """
        object["objuuid"] = objuuid
        object["coluuid"] = coluuid
        self.cursor.execute(
            "update TBL_JSON_OBJ set VALUE = ? where OBJUUID = ?;",
            (pickle.dumps(object), objuuid)
        )

        self.cursor.execute("delete from TBL_JSON_IDX where OBJUUID = ?;", (objuuid,))

        for attribute_name, attribute in self.list_attributes(coluuid).items():
            try:
                self.cursor.execute(
                    "insert into TBL_JSON_IDX (OBJUUID, COLUUID, ATTRIBUTE, VALUE)"\
                    "values (?, ?, ?, ?);",
                    (
                        objuuid, coluuid, attribute_name,
                        eval(f"str(self.get_object(objuuid){attribute})")
                    )
                )
            except: # pylint: disable=bare-except
                continue
        self.connection.commit()


    def get_object(self, objuuid):
        self.cursor.execute("select VALUE from TBL_JSON_OBJ where OBJUUID = ?;", (str(objuuid),))
        self.connection.commit()
        return pickle.loads(self.cursor.fetchall()[0][0])

    def find_objects(self, coluuid, attribute, value):
        self.cursor.execute("select OBJUUID from TBL_JSON_IDX where ATTRIBUTE = ? and VALUE = ? and COLUUID = ?;", \
                            (str(attribute), str(value), str(coluuid)))
        self.connection.commit()
        objuuids = []
        for row in self.cursor.fetchall():
            objuuids.append(row[0])
        return objuuids

    def delete_object(self, objuuid):
        try:
            self.cursor.execute("delete from TBL_JSON_OBJ where OBJUUID = ?;", (str(objuuid),))
        finally:
            self.connection.commit()


    def create_attribute(self, coluuid, attribute, path):
        try:
            self.cursor.execute("insert into TBL_JSON_ATTR (COLUUID, ATTRIBUTE, PATH) values (?, ?, ?);", \
                                (str(coluuid), str(attribute), str(path)))

            self.cursor.execute("delete from TBL_JSON_IDX where ATTRIBUTE = ? and COLUUID = ?;", (str(attribute), str(coluuid)))

            self.cursor.execute("select OBJUUID, VALUE from TBL_JSON_OBJ where COLUUID = ?;", (str(coluuid),))

            objects = {}
            for row in self.cursor.fetchall():
                objects[row[0]] = pickle.loads(row[1])

            for objuuid in objects:
                try:
                    self.cursor.execute("""insert into TBL_JSON_IDX (OBJUUID, COLUUID, ATTRIBUTE, VALUE)
                                        values (?, ?, ?, ?);""", \
                                        (str(objuuid), \
                                         str(coluuid), \
                                         str(attribute), \
                                         str(eval("str(objects[objuuid]" + path + ")"))))
                except:
                    continue
        except:
            pass
        finally:
            self.connection.commit()


    def delete_attribute(self, coluuid, attribute):
        try:
            self.cursor.execute("delete from TBL_JSON_ATTR where COLUUID = ? and ATTRIBUTE = ?;", \
                                (str(coluuid), str(attribute)))
        finally:
            self.connection.commit()


    def list_attributes(self, coluuid):
        self.cursor.execute("select ATTRIBUTE, PATH from TBL_JSON_ATTR where COLUUID = ?;", (str(coluuid),))
        self.connection.commit()

        attributes = {}
        for row in self.cursor.fetchall():
            attributes[row[0]] = row[1]
        return attributes

    def create_collection(self, uuid=None, name="New Collection"):
        try:
            if not uuid:
                uuid = get_uuid_str()

            self.cursor.execute("insert into TBL_JSON_COL (COLUUID, NAME) values (?, ?);", \
                                (str(uuid), str(name)))
        finally:
            self.connection.commit()

        return uuid

    def delete_collection(self, uuid):
        try:
            self.cursor.execute("delete from TBL_JSON_COL where COLUUID = ?;", (str(uuid),))
        finally:
            self.connection.commit()

    def list_collections(self):
        self.cursor.execute("select NAME, COLUUID from TBL_JSON_COL;")
        self.connection.commit()

        collections = {}
        for row in self.cursor.fetchall():
            collections[row[0]] = row[1]
        return collections

    def list_collection_objects(self, coluuid):
        self.cursor.execute("select OBJUUID from TBL_JSON_OBJ where COLUUID = ?;", (coluuid,))
        self.connection.commit()

        objuuids = []
        for row in self.cursor.fetchall():
            objuuids.append(row[0])
        return objuuids

    def list_objects(self):
        self.cursor.execute("select OBJUUID from TBL_JSON_OBJ;")
        self.connection.commit()

        objuuids = []
        for row in self.cursor.fetchall():
            objuuids.append(row[0])
        return objuuids

    def __del__(self):
        self.connection.close()

class Object(Document):
    def __init__(self, coluuid, objuuid, connection_str=DEFAULT_CONNECTION_STR):
        Document.__init__(self, connection_str=connection_str)

        self.objuuid = objuuid
        self.coluuid = coluuid
        self.load()

    def load(self):
        try:
            self.object = Document.get_object(self, self.objuuid)
        except IndexError:
            Document.create_object(self, self.coluuid, self.objuuid)
            self.object = Document.get_object(self, self.objuuid)

    def set(self):
        Document.set_object(self, self.coluuid, self.objuuid, self.object)

    def destroy(self):
        Document.delete_object(self, self.objuuid)
        self.object = None

class Collection(Document):
    def __init__(self, collection_name, connection_str=None):
        self.collection_name = collection_name
        if connection_str is None:
            self.connection_str = f'{collection_name}.sqlite'
        else:
            self.connection_str = connection_str

        Document.__init__(self, connection_str=self.connection_str)

        try:
            self.coluuid = Document.list_collections(self)[self.collection_name]
        except KeyError:
            self.coluuid = Document.create_collection(self, name = self.collection_name)

    def destroy(self):
        Document.delete_collection(self, self.coluuid)

    def create_attribute(self, attribute, path):
        Document.create_attribute(self, self.coluuid, attribute, path)

    def delete_attribute(self, attribute):
        Document.delete_attribute(self, self.coluuid, attribute)

    def find(self, **kargs):
        objuuid_sets = []

        if len(kargs) == 0:
            objuuid_sets.append(self.list_objuuids())

        for attribute, value in kargs.items():
            objuuid_sets.append(Document.find_objects(self, self.coluuid, attribute, value))

        intersection = set(objuuid_sets[0])
        for objuuids in objuuid_sets[1:]:
            intersection = intersection.intersection(set(objuuids))

        objects = []
        for objuuid in list(intersection):
            objects.append(Object(self.coluuid, objuuid, connection_str=self.connection_str))

        return objects

    def find_objuuids(self, **kargs):
        objuuid_sets = []

        if len(kargs) == 0:
            objuuid_sets.append(self.list_objuuids())

        for attribute, value in kargs.items():
            objuuid_sets.append(Document.find_objects(self, self.coluuid, attribute, value))

        intersection = set(objuuid_sets[0])
        for objuuids in objuuid_sets[1:]:
            intersection = intersection.intersection(set(objuuids))

        objuuids = []
        for objuuid in list(intersection):
            objuuids.append(objuuid)

        return objuuids

    def get_object(self, objuuid = None):
        if not objuuid:
            objuuid = get_uuid_str()
        return Object(self.coluuid, objuuid, connection_str=self.connection_str)

    def list_objuuids(self):
        return Document.list_collection_objects(self, self.coluuid)
