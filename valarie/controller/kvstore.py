#!/usr/bin/python3
"""This module implements functions for getting, setting, touching,
and delete keys in the key value store."""
from random import random
from typing import Any

from valarie.dao.document import Collection

def get(name: str, default: Any = None) -> Any:
    """This function gets the value at the key specified.

    Args:
        name:
            The name of the key being read.

        default:
            The default value if the key doesn't exist yet.
    """
    kvstore = Collection("kvstore")

    try:
        key = kvstore.find(name=name)[0]
    except IndexError:
        key = kvstore.get_object()
        key.object["name"] = name
        key.object["value"] = default
        key.set()

    try:
        return key.object["value"]
    except KeyError:
        key.object["value"] = default
        key.set()
        return default

def set(name: str, value: Any):
    """This function sets a value at the key specified.

    Args:
        name:
            The name of the key being set.

        value:
            The value to set the key to.
    """
    kvstore = Collection("kvstore")

    try:
        key = kvstore.find(name=name)[0]
    except IndexError:
        key = kvstore.get_object()

    key.object["name"] = name
    key.object["value"] = value
    key.set()

def touch(key: str) -> float:
    """This function touches the key specified by setting
    it to a random float.

    Args:
        name:
            The name of the key being set.
    """
    return set(key, random())

def delete(name: str):
    """This function deletes the key specified.

    Args:
        name:
            The name of the key being deleted.
    """
    try:
        key = Collection("kvstore").find(name=name)[0]
        key.destroy()
    except IndexError:
        pass

kvstore = Collection("kvstore")
kvstore.create_attribute("name", "['name']")
