#!/usr/bin/python3
"""This module implements the Document, Collection, and Object classes.
The document class wraps and abstracts the database and the various SQL
driving functions. It serves as the base class with is inherited by the
Collection and Object classes."""
import sqlite3
import pickle
from typing import Dict, List

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

        # pylint: disable=line-too-long
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TBL_JSON_OBJ (
                               OBJUUID VARCHAR(36),
                               COLUUID VARCHAR(36),
                               VALUE BLOB NOT NULL,
                               PRIMARY KEY (OBJUUID),
                               FOREIGN KEY (COLUUID) REFERENCES TBL_JSON_COL(COLUUID) ON DELETE CASCADE);''')

        # pylint: disable=line-too-long
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS TBL_JSON_ATTR (
                               COLUUID VARCHAR(36),
                               ATTRIBUTE VARCHAR(64),
                               PATH VARCHAR(64),
                               PRIMARY KEY (COLUUID, ATTRIBUTE),
                               FOREIGN KEY (COLUUID) REFERENCES TBL_JSON_COL(COLUUID) ON DELETE CASCADE);''')

        # pylint: disable=line-too-long
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
        UUIDs, the object is empty.  Objects being
        stored are pickled and serialized.

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
        self.connection.commit()

    def set_object(self, coluuid: str, objuuid: str, updated_object: Dict):
        """This function updates an object in a collection. The object dictionary,
        object UUID, and collection UUID are updated. In addition, previously indexed
        attributes are deleted and reset based on the updated object. Objects being
        stored are pickled and serialized.

        Args:
            coluuid:
                The collection UUID.

            objuuid:
                The object UUID.

            object:
                The object dictionary that will be stored.
        """
        updated_object["objuuid"] = objuuid
        updated_object["coluuid"] = coluuid
        self.cursor.execute(
            "update TBL_JSON_OBJ set VALUE = ? where OBJUUID = ?;",
            (pickle.dumps(updated_object), objuuid)
        )

        self.cursor.execute("delete from TBL_JSON_IDX where OBJUUID = ?;", (objuuid,))

        for attribute_name, attribute in self.list_attributes(coluuid).items():
            try:
                self.cursor.execute(
                    "insert into TBL_JSON_IDX (OBJUUID, COLUUID, ATTRIBUTE, VALUE)"\
                    "values (?, ?, ?, ?);",
                    (
                        objuuid, coluuid, attribute_name,
                        # pylint: disable=eval-used
                        eval(f"str(self.get_object(objuuid){attribute})")
                    )
                )
            except (KeyError, ValueError):
                continue
        self.connection.commit()

    def get_object(self, objuuid: str) -> Dict:
        """Select, load, and deserialize an object. Pickle is used to deserialize and
        load the object.

        Args:
            objuuid:
                An object's UUID.

        Returns:
            A dictionary of the object.

        Raises:
            IndexError:
                This is raised when a requested object does not exist.
        """
        self.cursor.execute("select VALUE from TBL_JSON_OBJ where OBJUUID = ?;", (objuuid,))
        self.connection.commit()
        return pickle.loads(self.cursor.fetchall()[0][0])

    def find_objects(self, coluuid: str, attribute: str, value: str) -> List[str]:
        """This function finds a list of object UUIDs by matching a value to an
        indexed attribute.

        Args:
            coluuid:
                The UUID of the collection to search against.

            attribute:
                The name of the attribute to search against.

            value:
                The value of the attribute to match on.

        Returns:
            A list of UUID strings.
        """
        self.cursor.execute(
            "select OBJUUID from TBL_JSON_IDX where ATTRIBUTE = ? and VALUE = ? and COLUUID = ?;",
            (attribute, value, coluuid)
        )
        self.connection.commit()
        objuuids = []
        for row in self.cursor.fetchall():
            objuuids.append(row[0])
        return objuuids

    def delete_object(self, objuuid: str):
        """This function deletes an object.

        Args:
            objuuid:
                The object's UUID."""
        self.cursor.execute("delete from TBL_JSON_OBJ where OBJUUID = ?;", (objuuid,))
        self.connection.commit()

    def create_attribute(self, coluuid: str, attribute: str, path: str):
        """This function creates a new attribute for a collection. Upon creation of
        the attribute, all of the collection's objects are indexed with the new
        attribute.

        The attribute path is one or multiple index operators used to select a key or
        index out of a dictionary.

            ["inner"]["outer"]

        Args:
            coluuid:
                The collection UUID.

            attribute:
                The attribute name.

            path:
                The attribute path.
        """
        self.cursor.execute(
            "insert into TBL_JSON_ATTR (COLUUID, ATTRIBUTE, PATH) values (?, ?, ?);",
            (coluuid, attribute, path)
        )

        self.cursor.execute(
            "select OBJUUID, VALUE from TBL_JSON_OBJ where COLUUID = ?;", (coluuid,)
        )

        for row in self.cursor.fetchall():
            try:
                self.cursor.execute(
                    "insert into TBL_JSON_IDX (OBJUUID, COLUUID, ATTRIBUTE, VALUE)"\
                    "values (?, ?, ?, ?);",
                    # pylint: disable=eval-used
                    (row[0], coluuid, attribute, eval(f"str(pickle.loads(row[1]){path})"))
                )
            except (KeyError, ValueError):
                continue

        self.connection.commit()

    def delete_attribute(self, coluuid: str, attribute: str):
        """This function delete an attribute from a collection.

        Args:
            coluuid:
                The collection UUID.

            attribute:
                The attribute name.
        """
        self.cursor.execute(
            "delete from TBL_JSON_ATTR where COLUUID = ? and ATTRIBUTE = ?;",
            (coluuid, attribute)
        )

        self.cursor.execute(
            "delete from TBL_JSON_IDX where ATTRIBUTE = ? and COLUUID = ?;",
            (attribute, coluuid)
        )

        self.connection.commit()


    def list_attributes(self, coluuid: str) -> Dict[str, str]:
        """This function returns a dictionary of a collection's attribute names
        and corresponding attribute paths.

        Args:
            coluuid:
                The collection's UUID.

        Returns:
            A dictionary of attribute paths keyed by their attribute names.
        """
        self.cursor.execute(
            "select ATTRIBUTE, PATH from TBL_JSON_ATTR where COLUUID = ?;",
            (coluuid,)
        )

        self.connection.commit()

        attributes = {}
        for row in self.cursor.fetchall():
            attributes[row[0]] = row[1]
        return attributes

    def create_collection(self, name: str) -> str:
        """This function creates a new collection and returns its UUID.

        Args:
            name:
                Name of the collection.

        Returns:
            coluuid:
                The collection's UUID.
        """
        coluuid = get_uuid_str()

        self.cursor.execute(
            "insert into TBL_JSON_COL (COLUUID, NAME) values (?, ?);",
            (coluuid, name)
        )

        self.connection.commit()

        return coluuid

    def delete_collection(self, coluuid: str):
        """This function deletes a collection.

        Args:
            coluuid:
                The collection's UUID.
        """
        self.cursor.execute("delete from TBL_JSON_COL where COLUUID = ?;", (coluuid,))
        self.connection.commit()

    def list_collections(self) -> Dict[str, str]:
        """This function returns a dictionary of the collection UUIDs
        keyed with collection names.

        Returns:
            A dictionary of names and collection UUIDs.
        """
        self.cursor.execute("select NAME, COLUUID from TBL_JSON_COL;")
        self.connection.commit()

        collections = {}
        for row in self.cursor.fetchall():
            collections[row[0]] = row[1]
        return collections

    def list_collection_objects(self, coluuid: str) -> List[str]:
        """This function returns a list of object UUIDs present in the collection..

        Returns:
            A list of object UUIDs.
        """
        self.cursor.execute("select OBJUUID from TBL_JSON_OBJ where COLUUID = ?;", (coluuid,))
        self.connection.commit()
        return [row[0] for row in self.cursor.fetchall()]

    def __del__(self):
        """This destructor function closes the database connection."""
        self.connection.close()

class Object(Document):
    """This class encapsulates a collection object and implements methods
    for construction, loading, setting, and destroying collection objects."""
    def __init__(self, coluuid: str, objuuid: str, connection_str: str = DEFAULT_CONNECTION_STR):
        """This function initilizes an instance of a collection object. It
        initializes a document instance and loads the object from it.

        Args:
            coluuid:
                The collection UUID.

            objuuid:
                The object UUID.

            connection_str:
                The sqlite connection string the document instance will use."""
        Document.__init__(self, connection_str=connection_str)
        self.objuuid = objuuid
        self.coluuid = coluuid
        self.object = None
        self.load()

    def load(self):
        """Load an existing or create a new object and load."""
        try:
            self.object = Document.get_object(self, self.objuuid)
        except IndexError:
            Document.create_object(self, self.coluuid, self.objuuid)
            self.object = Document.get_object(self, self.objuuid)

    def set(self):
        """Commit the object's state to the database."""
        Document.set_object(self, self.coluuid, self.objuuid, self.object)

    def destroy(self):
        """Remove the object from the database."""
        Document.delete_object(self, self.objuuid)
        self.object = None

class Collection(Document):
    """This class implements the document object collection. This is the primary
    interface for searching and accessing objects."""
    def __init__(self, collection_name: str, connection_str: str = None):
        """This method contructs a collection instance. A collection name and
        optionally a sqlite connection string is used for resolving or creating
        a new document collection.

        Args:
            collection_name:
                A collection's name.

            connection_str:
                A sqlite connection str.
        """
        self.collection_name = collection_name
        if connection_str is None:
            self.connection_str = f'{collection_name}.sqlite'
        else:
            self.connection_str = connection_str

        Document.__init__(self, connection_str=self.connection_str)

        try:
            self.coluuid = Document.list_collections(self)[self.collection_name]
        except KeyError:
            self.coluuid = Document.create_collection(self, self.collection_name)

    def destroy(self):
        """This method deletes the collection from the database."""
        Document.delete_collection(self, self.coluuid)

    # pylint: disable=arguments-differ
    def create_attribute(self, attribute: str, path: str):
        """This method creates or updates an attribute for the collection
        to indexed on. If an attribute is updated, the existing index state for the
        attribute is deleted and then rebuilt. The key to be indexed on is expressed
        as a series of index operators:

            ["key1"][1]["key2"]

        Args:
            attribute:
                Name of the attribute.

            path:
                The object path to index on."""
        attributes = Document.list_attributes(self, self.coluuid)
        if (
                (attribute in attributes.keys() and attributes[attribute] != path) or
                attribute not in attributes.keys()
            ):
            self.delete_attribute(attribute)
            Document.create_attribute(self, self.coluuid, attribute, path)

    # pylint: disable=arguments-differ
    def delete_attribute(self, attribute: str):
        """This method deletes an attribute from the collection.

        Args:
            attribute:
                Name of the attribute.
        """
        Document.delete_attribute(self, self.coluuid, attribute)

    def find(self, **kargs: Dict[str, str]) -> List[Object]:
        """This method finds and returns a list of collection objects by matching attribute
        values to the key word arguments applied to this method. The key maps to the attribute
        name and the value maps to the indexed attribute value.

        Args:
            **kargs:
                Dictionary of attribute strings.

        Returns:
            A list of collection objects.
        """
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

    def find_objuuids(self, **kargs: Dict[str, str]) -> List[str]:
        """This method finds and returns a list of collection object UUIDs by matching attribute
        values to the key word arguments applied to this method. The key maps to the attribute
        name and the value maps to the indexed attribute value.

        Args:
            **kargs:
                Dictionary of attribute strings.

        Returns:
            A list of collection object UUIDs.
        """
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

    def get_object(self, objuuid: str = None) -> Object:
        """This method returns a new or existing collection object. If an object UUID is
        not specified, then a UUID is generated.

        Args:
            objuuid:
                A object UUID.

        Returns:
            A collection object.
        """
        return Object(
            self.coluuid,
            get_uuid_str() if objuuid is None else objuuid,
            connection_str=self.connection_str
        )

    def list_objuuids(self) -> List[str]:
        """This method returns a list of every object UUID in the collection.

        Returns:
            A list of object UUIDs.
        """
        return Document.list_collection_objects(self, self.coluuid)
