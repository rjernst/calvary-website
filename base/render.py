
from google.appengine.ext.webapp import template
import os
import re

_req_re = re.compile(r'/([^/]+)(/[^/]+)?.*')

class Link(object):
    def __init__(self, url, name, handler):
        self.url = url
        self.name = name
        self.handler = handler

def render(handler, file, args):
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
    page = req.group(2) or ''
    args['page'] = page

    if file is None:
        file = '../html/%s.%s.html' % (site, page)
        if not os.path.exists(file):
            file = '../html/stub.html'
    handler.response.out.write(template.render(file, args))

    
