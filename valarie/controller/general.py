#!/usr/bin/python3
"""This module implements the restart function used for restarting valarie."""

from valarie.controller.config import get_config
from valarie.controller import logging
from valarie.executor.system import system

def restart() -> int:
    """This function restarts valarie.

    Returns:
        The restart commands return code as an integer.
    """
    logging.info("restarting...")
    return system(get_config()["restartcmd"])
