#!/usr/bin/python3
"""This module implements the routes for posting and reading messages to the
message board displayed in the UI."""
from typing import Dict, List

import cherrypy

from valarie.controller.messaging import add_message, get_messages

class Messaging():
    """This class registers the endpoint methods as endpoints."""
    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def add_message(cls, message: str, timestamp: float) -> Dict:
        """This function registers the endpoint that posts a
        message with a timestamp.

        Args:
            message:
                Message string.

            timestamp:
                10 digit epoch timestamp.
        """
        add_message(message, timestamp)
        return {}

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def add_message(cls, message: str) -> Dict:
        """This function registers the endpoint that posts a message.

        Args:
            message:
                Message string.

        """
        add_message(message)
        return {}

    @classmethod
    @cherrypy.expose
    @cherrypy.tools.json_out()
    def get_messages(cls) -> List[Dict]:
        """This function registers the endpoint returns a list of the messages.

        Returns:
            A list of message strings.
        """
        return get_messages()

