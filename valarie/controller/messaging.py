#!/usr/bin/python3
"""This module implements functions for adding and getting messages."""
from typing import Dict, List

from valarie.controller import kvstore

def add_message(message: str):
    """This is a function used to add a message to the messages key in
    the key-value store collection. The message list is capped and
    roles over at a length of 50.

    Args:
        message:
            A message string.
    """
    messages = kvstore.get("messages", [])
    messages = [message] + messages[:49]
    kvstore.set("messages", messages)

def get_messages() -> List[Dict]:
    """This is a function used to retrieve the messages from key value store.

    Returns:
        A list of message dictionaries.
    """
    return kvstore.get("messages", [])
