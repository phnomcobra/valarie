#!/usr/bin/python3
"""This module implements system for the executor module."""

from subprocess import Popen, PIPE

from valarie.controller import logging

def system(command: str) -> int:
    """This function executes a command on the system.
    Standard out and standard error emit into the logger.

        Args:
            command:
                The command to execute.

        Returns:
            Returns the return code as an integer.
        """
    logging.info(command)

    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    output_buffer, stderr_buffer = process.communicate()
    stdout, stderr = str(output_buffer.decode()).strip(), str(stderr_buffer.decode()).strip()

    if len(stdout) > 0:
        logging.debug(stdout)

    if len(stderr) > 0:
        logging.error(stderr)

    logging.info(f'returned {process.returncode}')

    return process.returncode
