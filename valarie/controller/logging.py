"""This module forms the interface for logging."""
from datetime import datetime
from enum import Enum
import logging
import logging.handlers
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

def critical(item: Any = ''):
    """This function logs a critical item in the application log.

    Args:
        item:
            Anything that has __str__.
    """
    _log(item, LogLevel.CRITICAL)

def error(item: Any = ''):
    """This function logs a error item in the application log.

    Args:
        item:
            Anything that has __str__.
    """
    _log(item, LogLevel.ERROR)

def warning(item: Any = ''):
    """This function logs a warning item in the application log.

    Args:
        item:
            Anything that has __str__.
    """
    _log(item, LogLevel.WARNING)

def info(item: Any = ''):
    """This function logs a information item in the application log.

    Args:
        item:
            Anything that has __str__.
    """
    _log(item, LogLevel.INFO)

def debug(item: Any = ''):
    """This function logs a debugging item in the application log.

    Args:
        item:
            Anything that has __str__.
    """
    _log(item, LogLevel.DEBUG)

def log(item: Any = ''):
    """This function logs an item in the application log.

    Args:
        item:
            Anything that has __str__.
    """
    _log(item)

def _log(item: Any, level: LogLevel = LogLevel.NOTSET):
    """This is a dunder method for handling all the application log events. It has a
    dual functionality. It formats and logs lines via the builtin logger and it
    formats and logs lines via `add_message` which is registered in the front end
    consoles. Inspect is use to read the caller's stack frame to indicate a file and
    function that's generating the log entry. This function is not called directly so that
    that stack frame 2 is caller's frame.

    Args:
        item:
            Anything that has __str__.

        level:
            A `LogLevel` enum indicating what log level to use.
    """
    logger = logging.getLogger('app')
    lines = str(item).split("\n")

    frame = stack()[2]

    short_filename = '/'.join(frame.filename.strip().split('/')[-2:])
    function = frame.function
    datetime_str = datetime.now().strftime('%Y-%m-%d|%H:%M:%S')

    for line in lines:
        log_line = f'{level.name}|{datetime_str}|{short_filename}|{function}|{line}'

        if level is LogLevel.CRITICAL:
            logger.critical(log_line)
        elif level is LogLevel.ERROR:
            logger.error(log_line)
        elif level is LogLevel.WARNING:
            logger.warning(log_line)
        elif level is LogLevel.INFO:
            logger.info(log_line)
        elif level is LogLevel.DEBUG:
            logger.debug(log_line)

        message_line = f'{short_filename}|{function}|{line}'
        if level in (LogLevel.CRITICAL, LogLevel.ERROR):
            add_message(f'<font color="red">{message_line}</font>')
        elif level is LogLevel.WARNING:
            add_message(f'<font color="orange">{message_line}</font>')
        elif level is LogLevel.INFO:
            add_message(f'<font color="green">{message_line}</font>')
        elif level is LogLevel.DEBUG:
            add_message(f'<font color="blue">{message_line}</font>')
        else:
            add_message(message_line)
