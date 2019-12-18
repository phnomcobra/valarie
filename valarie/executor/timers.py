#!/usr/bin/python

from valarie.controller.messaging import add_message

timers = {}

def cancel_timers():
    for key in timers.keys():
        try:
            timers[key].cancel()
            add_message(f"Cancelling {key}...OK")
        except Exception as e:
            msg = str(e)
            add_message(f"Cancelling {key}...{msg}")
