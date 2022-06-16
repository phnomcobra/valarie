#!/usr/bin/python3
"""This module implements the restart function used for restarting valarie."""

from valarie.controller.config import get_config
from valarie.executor.system import system
from valarie.router.messaging import add_message

def restart() -> int:
    """This function restarts valarie.

    Returns:
        The restart commands return code as an integer.
    """
    add_message("Restarting...")
    return system(get_config()["restartcmd"])
