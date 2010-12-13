import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

from google.appengine.api import users

FB_KEY = '183464395004093'

class Login(webapp.RequestHandler):
  def get(self):
    next = self.request.get('next', '/auth/account')
    logging.info('creating login form, next: %s' % next)
    vars = { 'next': next, }

    self.tpl('login.html', vars)

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

  def tpl(self, tpl_file, vars = {}):
      vars['fb_key'] = FB_KEY
      path = os.path.join(os.path.dirname(__file__), 'templates/' + tpl_file)
      self.response.out.write(template.render(path, vars))

application = webapp.WSGIApplication([('/auth/login', Login)], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
