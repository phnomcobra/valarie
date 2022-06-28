#!/usr/bin/python3
from random import random
from typing import Any

from valarie.dao.document import Collection

def get(name: str, default: Any = None) -> Any:
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
    kvstore = Collection("kvstore")

    try:
        key = kvstore.find(name=name)[0]
    except IndexError:
        key = kvstore.get_object()

    key.object["name"] = name
    key.object["value"] = value
    key.set()

def touch(key: str) -> float:
    return set(key, random())

def delete(name: str):
    try:
        key = Collection("kvstore").find(name=name)[0]
        key.destroy()
    except IndexError:
        pass

kvstore = Collection("kvstore")
kvstore.create_attribute("name", "['name']")
