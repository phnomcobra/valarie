"""This module forms the interface for logging."""
from datetime import datetime
from enum import Enum
import logging
from inspect import stack
from typing import Any

from valarie.controller.messaging import add_message

class LogLevel(Enum):
    """This class is enum for the listed log levels."""
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    NOTSET = 0

def critical(item: Any):
    log(item, LogLevel.CRITICAL)

def error(item: Any):
    log(item, LogLevel.ERROR)

def warning(item: Any):
    log(item, LogLevel.WARNING)

def info(item: Any):
    log(item, LogLevel.INFO)

def debug(item: Any):
    log(item, LogLevel.DEBUG)

def log(item: Any, level: LogLevel = LogLevel.NOTSET):
    lines = str(item).split("\n")

    frame = stack()[2]

    short_filename = '/'.join(frame.filename.strip().split('/')[-2:])
    function = frame.function
    datetime_str = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')

    for line in lines:
        formatted_line = f'{level.name}|{datetime_str}|{short_filename}|{function}|{line}'

        if level is LogLevel.CRITICAL:
            logging.critical(formatted_line)
        elif level is LogLevel.ERROR:
            logging.error(formatted_line)
        elif level is LogLevel.WARNING:
            logging.warning(formatted_line)
        elif level is LogLevel.INFO:
            logging.info(formatted_line)
        elif level is LogLevel.DEBUG:
            logging.debug(formatted_line)

        if level in (LogLevel.CRITICAL, LogLevel.ERROR):
            add_message(f'<font color="red">{formatted_line}</font>')
        elif level is LogLevel.WARNING:
            add_message(f'<font color="yellow">{formatted_line}</font>')
        elif level is LogLevel.INFO:
            add_message(f'<font color="green">{formatted_line}</font>')
        elif level is LogLevel.DEBUG:
            add_message(f'<font color="blue">{formatted_line}</font>')
        else:
            add_message(formatted_line)
