#!/usr/bin/python3
"""This module implements a wrapper around a UUID generator."""

from uuid import uuid4

def get_uuid_str() -> str:
    """This function generates a UUID string.

    Returns:
        A UUID as a string.
    """
    return str(uuid4())
