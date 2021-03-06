#!/usr/bin/python

import jinja2

from valarie.model.config import get_config

def index_view():
    templateLoader = jinja2.FileSystemLoader(searchpath = "./valarie/view/templates")
    templateEnv = jinja2.Environment(loader = templateLoader)
    template = templateEnv.get_template('index.html')
    return template.render(brand=get_config()["brand"])
    