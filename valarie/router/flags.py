#!/usr/bin/python3
"""This module implements the flag routes used to
signal the UI to take some action on a flag being changed."""

from typing import Any, Dict

import cherrypy

from valarie.controller.flags import get_flag, set_flag, touch_flag

class Flags():
    """This class encapsulates the flag routes."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def set(cls, key: str, value: Any) -> Dict:
        """This function sets the value of a flag and returns the key and value.

        Args:
            key:
                Key name of the flag.

            value:
                Value to set the flag to.

        Returns:
            JSON string of the flag's key and value.
        """
        return {
            "key" : key,
            "value" : set_flag(key, value)
        }

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get(cls, key: str) -> Dict:
        """This function gets the value of a flag and returns the key and value.

        Args:
            key:
                Key name of the flag.

        Returns:
            JSON string of the flag's key and value.
        """
        return {
            "key" : key,
            "value" : get_flag(key)
        }

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def touch(cls, key: str) -> Dict:
        """This function touches the value of a flag and returns the key and value.

        Args:
            key:
                Key name of the flag.

        Returns:
            JSON string of the flag's key and value.
        """
        return {
            "key" : key,
            "value" : touch_flag(key)
        }
