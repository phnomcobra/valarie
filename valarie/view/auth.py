#!/usr/bin/python

import jinja2

from valarie.model.config import get_config

def login_view():
    config = get_config()
    templateLoader = jinja2.FileSystemLoader(searchpath = "./valarie/view/templates")
    templateEnv = jinja2.Environment(loader = templateLoader)
    template = templateEnv.get_template('login.html')
    return template.render(title=config["title"], banner=config["banner"])