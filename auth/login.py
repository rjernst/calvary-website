import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import users
from auth import tpl

FB_KEY = '183464395004093'

class Login(webapp.RequestHandler):
  def get(self):
    next = self.request.get('next', '/auth/account')
    logging.info('creating login form, next: %s' % next)
    vars = { 'next': next, 'fb_key': FB_KEY}

    tpl(self, 'login.html', vars)

  def post(self):
    next = self.request.get('next')
    logging.info('Login handler called, next: %s' % next)
    openid = self.request.get('openid_url')
    if openid:
      logging.info('creating login url for openid: %s' % openid)
      login_url = users.create_login_url(next, federated_identity=openid)
      logging.info('redirecting to url: %s' % login_url)
      self.redirect(login_url)
    else:
      self.error(400)

class Login2(webapp.RequestHandler):

  def get(self):
    openid = self.request.get('openid_url')
    if openid:
      logging.info('creating login url for openid: %s' % openid)
      next = '/auth/login3?next=%s' % self.request.get('next')
      login_url = users.create_login_url(next, federated_identity=openid)
      logging.info('redirecting to url: %s' % login_url)
      self.redirect(login_url)
    else:
      self.error(400)

class Login3(webapp.RequestHandler):

  def get(self):
    tpl(self, 'complete_login.html', {'next': self.request.get('next')})

application = webapp.WSGIApplication([
    ('/auth/login', Login),
    ('/auth/login2', Login2),
    ('/auth/login3', Login3),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
