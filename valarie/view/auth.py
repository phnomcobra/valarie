#!/usr/bin/python

import jinja2

def admin_view():
    templateLoader = jinja2.FileSystemLoader(searchpath = "./valarie/view/templates")
    templateEnv = jinja2.Environment(loader = templateLoader )
    template = templateEnv.get_template('auth.html')
    return template.render()
    
def login_view(username, msg = "Enter login information", from_page = "/"):
    templateLoader = jinja2.FileSystemLoader(searchpath = "./valarie/view/templates")
    templateEnv = jinja2.Environment(loader = templateLoader)
    template = templateEnv.get_template('login.html')
    return template.render(username = username, msg = msg, from_page = from_page)