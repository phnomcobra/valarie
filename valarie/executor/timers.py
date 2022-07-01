#!/usr/bin/python3
"""This module encapsulates the timers dictionary and implements
timer cancellation."""

from valarie.router.messaging import add_message

timers = {}

def cancel_timers():
    """This function enumerates the timers and attempts to cancel
    each timer."""
    for key in timers.keys(): # pylint: disable=consider-iterating-dictionary
        try:
            timers[key].cancel()
            add_message(f"CANCELLING {key}...OK")
        except Exception as exception:
            msg = str(exception)
            add_message(f"CANCELLING {key}...{msg}")
