#!/usr/bin/python3

from threading import Lock
from random import random
from copy import deepcopy

flags = {}
flag_lock = Lock()

def set_flag(key, value):
    flag_lock.acquire()
    flags[key] = deepcopy(value)
    flag_lock.release()
    return value

def get_flag(key):
    try:
        flag_lock.acquire()
        value = deepcopy(flags[key])
    except KeyError:
        flags[key] = random()
        value = deepcopy(flags[key])
    finally:
        flag_lock.release()
        return value

def touch_flag(key):
    return set_flag(key, random())
