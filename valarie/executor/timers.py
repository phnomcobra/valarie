#!/usr/bin/python3
"""This module encapsulates the timers dictionary and implements
timer cancellation."""

from valarie.router.messaging import add_message

TIMERS = {}

def cancel_timers():
    """This function enumerates the timers and attempts to cancel
    each timer."""
    for key in TIMERS.keys(): # pylint: disable=consider-iterating-dictionary
        try:
            TIMERS[key].cancel()
            add_message(f"CANCELLING {key}...OK")
        except Exception as exception: # pylint: disable=broad-except
            add_message(f"CANCELLING {key}...{str(exception)}")
