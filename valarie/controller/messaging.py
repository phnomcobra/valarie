#!/usr/bin/python3
"""This module implements functions for adding and getting messages."""
from time import time, strftime, localtime
from typing import Dict, List

from valarie.controller import kvstore

def add_message(message: str, timestamp: float = None):
    """This is a function used to add a message to the messages key in
    the key-value store collection. The message list is capped and
    roles over at a length of 50.

    Args:
        message:
            A message string.

        timestamp:
            10 digit epoch time stamp.
    """
    if not timestamp:
        timestamp = time()

    messages = kvstore.get("messages", [])

    messages = [
        {
            "message": message,
            "timestamp": strftime('%H:%M:%S', localtime(timestamp))
        }
    ] + messages[:49]

    kvstore.set("messages", messages)

def get_messages() -> List[Dict]:
    """This is a function used to retrieve the messages from key value store.

    Returns:
        A list of message dictionaries.
    """
    return kvstore.get("messages", [])
