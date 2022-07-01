#!/usr/bin/python3
"""The module implements the templating functions for serving HTML."""

import jinja2

from valarie.controller.config import get_config

def index_view() -> str:
    """This function interpolates the index HTML.

    Returns:
        String of the interpolated HTML.
    """
    loader = jinja2.FileSystemLoader(searchpath="./valarie/view/templates")
    environent = jinja2.Environment(loader=loader)
    template = environent.get_template('index.html')
    return template.render(brand=get_config()["brand"])
