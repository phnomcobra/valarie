#!/usr/bin/python

import jinja2

from valarie.dao.document import Collection
from valarie.model.config import CONFIG_OBJUUID

def login_view():
    config = Collection("inventory").get_object(CONFIG_OBJUUID)
    templateLoader = jinja2.FileSystemLoader(searchpath = "./valarie/view/templates")
    templateEnv = jinja2.Environment(loader = templateLoader)
    template = templateEnv.get_template('login.html')
    return template.render(title=config.object["title"], banner=config.object["banner"])