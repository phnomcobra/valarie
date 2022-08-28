#!/usr/bin/python3
"""This module implements a wrapper around a UUID generator."""
from hashlib import sha256
from uuid import uuid4

def get_uuid_str() -> str:
    """This function generates a UUID string.

    Returns:
        A UUID as a string.
    """
    return str(uuid4())

def get_uuid_str_from_str(seed: str) -> str:
    """This function generates a UUID from a string.

    Args:
        seed:
            String to be digested.

    Returns:
        A UUID as a string.
    """
    _hash = sha256()
    _hash.update(seed.encode())
    digest = _hash.hexdigest()
    return f'{digest[0:8]}-{digest[8:12]}-{digest[12:16]}-{digest[16:20]}-{digest[20:32]}'
