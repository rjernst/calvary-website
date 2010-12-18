import os
from google.appengine.ext import webapp

def tpl(handler, tpl_file, vars = {}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + tpl_file)
  handler.response.out.write(webapp.template.render(path, vars))
