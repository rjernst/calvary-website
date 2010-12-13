import os
import logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from auth import facebook
from google.appengine.ext import db, webapp
from google.appengine.api import users
from django.utils import simplejson as json

from google.appengine.api import users

FB_KEY = '183464395004093'
FB_SECRET = '34fc33154cc39b66900dafeadf313d85'
FB_API = facebook.Facebook(FB_KEY, FB_SECRET)
FB_LOGOUT = '<link rel="stylesheet" type="text/css" media="screen" href="openid.css" />'

class UserInfo(db.Model):
  provider = db.StringProperty()
  name = db.StringProperty()
  email = db.EmailProperty()
  groups = db.ListProperty(int)

def require_login(method):
  def call(handler):
    user_key = get_user_key(handler.request)
    if not user_key:
      logging.info("No user!!")
      handler.redirect('/auth/login')
    else:
      return method(handler)
  return call

def get_user_key(request):
  # TODO: need to store user in session
  guser = users.get_current_user()
  key = None
  if guser is not None:
    logging.info("federated login found")
    # logged in through federated login
    key = guser.federated_identity()
  elif FB_API.find_session(request):
    logging.info("facebook login found")
    # logged in through facebook
    # TODO: FB_API should not contain per session info
    key = 'fb_%s' % FB_API.uid
  return key

class View(webapp.RequestHandler):

  @require_login
  def get(self):
    user_key = get_user_key(self.request)
    user = UserInfo.get_by_key_name(user_key)
    if user is None:
      self.redirect('/auth/account/create')
    else:
      vars = {
        'name': user.name,
        'email': user.email,
        'uid': user.key().name(),
      }

      # TODO: add logout link
      tpl(self, 'account.html', vars)
      

# TODO: move this somewhere else
# XXX: is this really worth it? probably won't have too many forms
def check_form(handler, args):
  vals = []
  for arg in args:
    val = handler.request.get(arg)
    if val is None:
      handler.redirect(handler.url)
    vals.append(val)
  return vals

class Create(webapp.RequestHandler):
  
  @require_login
  def get(self):
    tpl(self, 'create.html')
    
  @require_login
  def post(self):
    user_key = get_user_key(self.request)
    user = UserInfo.get_by_key_name(user_key)
    if user:
      raise Exception("user %s already exists" % user_key) 

    vals = check_form(self, ['name', 'email'])

    user = UserInfo(key_name=user_key, name=vals[0], email=vals[1])
    user.put()
    self.redirect('/auth/account')

def tpl(handler, tpl_file, vars = {}):
  vars['fb_key'] = FB_KEY
  path = os.path.join(os.path.dirname(__file__), 'templates/' + tpl_file)
  handler.response.out.write(template.render(path, vars))

application = webapp.WSGIApplication([
    ('/auth/account/create', Create),
    ('/auth/account', View),
], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
