#!/usr/bin/python3
"""This module encapsulates the timers dictionary and implements
timer cancellation."""

from valarie.controller import logging

TIMERS = {}

def cancel_timers():
    """This function enumerates the timers and attempts to cancel
    each timer."""
    for key in TIMERS.keys(): # pylint: disable=consider-iterating-dictionary
        logging.info(f"cancelling {key}")
        try:
            TIMERS[key].cancel()
        except Exception as exception: # pylint: disable=broad-except
            logging.error(exception)
