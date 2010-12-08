
from google.appengine.ext.webapp import template
import os
import re
import logging
from google.appengine.api import users

_req_re = re.compile(r'/([^/]+)(/[^/]+)?.*')

class Link(object):
    def __init__(self, url, name, handler):
        self.url = url
        self.name = name
        self.handler = handler

def render(handler, file, args):
    user = users.get_current_user()
    if user:
        logging.info("User: %s, %s, %s, %s, %s" % (user.nickname(), user.email(), user.user_id(), user.federated_identity(), user.federated_provider()))
        if users.is_current_user_admin():
            logging.info("User is ADMIN")
    if 'links' not in args:
        if handler.request.path.startswith('/school'):
            import school.urls
            args['links'] = school.urls.links
        else:
            import church.urls
            args['links'] = church.urls.links    
    req = _req_re.match(handler.request.path)
    site = req.group(1)
    args['site'] = site
    page = req.group(2) or 'home'
    args['page'] = page[1:]
    args['logout'] = users.create_logout_url('/school')
    args['user'] = user

    if file is None:
        file = '../templates/%s.%s.html' % (site, page[1:])
        logging.info("Looking up page: %s" % file)
        if not os.path.exists(file):
            file = '../templates/stub.html'
    handler.response.out.write(template.render(file, args))

    
