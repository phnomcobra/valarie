#!/usr/bin/python3
"""This module implements system for the executor module."""

from subprocess import Popen, PIPE

from valarie.router.messaging import add_message

def system(command: str) -> int:
    """This function executes a command on the system.
    Standard out and standard error emit into the add_message route.

        Args:
            command:
                The command to execute.

        Returns:
            Returns the return code as an integer.
        """
    add_message(f'system: {command}')

    process = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    output_buffer, stderr_buffer = process.communicate()
    stdout, stderr = str(output_buffer.decode()).strip(), str(stderr_buffer.decode()).strip()

    if len(stdout) > 0:
        add_message(stdout)

    if len(stderr) > 0:
        add_message(f'<font color="red">{stderr}</font>')

    add_message(f'returned {process.returncode}')

    return process.returncode
