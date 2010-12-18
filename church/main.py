
from google.appengine.ext import webapp
from base.render import render

url = '../html/church.html'

class HomeHandler(webapp.RequestHandler):
    def get(self):
        render(self, url, {})
