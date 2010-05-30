
from google.appengine.ext import webapp
from base.render import render

url = '../html/school.html'

class HomeHandler(webapp.RequestHandler):
    def get(self):
        render(self, url, {})
