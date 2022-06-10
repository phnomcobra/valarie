#!/usr/bin/python3
"""This module implements the flag routes used to
signal the UI to take some action on a flag being changed."""

import json
from typing import Any

import cherrypy

from valarie.controller.flags import get_flag, set_flag, touch_flag

class Flags():
    """This class encapsulates the flag routes."""
    @classmethod
    @cherrypy.expose
    def set(cls, key: str, value: Any) -> str:
        """This function sets the value of a flag and returns the key and value.

        Args:
            key:
                Key name of the flag.

            value:
                Value to set the flag to.

        Returns:
            JSON string of the flag's key and value.
        """
        item = {
            "key" : key,
            "value" : set_flag(key, value)
        }
        return json.dumps(item)

    @classmethod
    @cherrypy.expose
    def get(cls, key: str) -> str:
        """This function gets the value of a flag and returns the key and value.

        Args:
            key:
                Key name of the flag.

        Returns:
            JSON string of the flag's key and value.
        """
        item = {
            "key" : key,
            "value" : get_flag(key)
        }
        return json.dumps(item)

    @classmethod
    @cherrypy.expose
    def touch(cls, key: str) -> str:
        """This function touches the value of a flag and returns the key and value.

        Args:
            key:
                Key name of the flag.

        Returns:
            JSON string of the flag's key and value.
        """
        item = {
            "key" : key,
            "value" : touch_flag(key)
        }
        return json.dumps(item)
