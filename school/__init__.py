
import os
from google.appengine.ext import webapp

def tpl(tpl_file, vars = {}):
  path = os.path.join(os.path.dirname(__file__), 'templates/' + tpl_file)
  return webapp.template.render(path, vars)
