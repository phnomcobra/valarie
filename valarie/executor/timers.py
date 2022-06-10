#!/usr/bin/python3

from valarie.router.messaging import add_message

timers = {}

def cancel_timers():
    for key in timers.keys():
        try:
            timers[key].cancel()
            add_message(f"CANCELLING {key}...OK")
        except Exception as e:
            msg = str(e)
            add_message(f"CANCELLING {key}...{msg}")
