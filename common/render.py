from google.appengine.ext.webapp.template import render, Template
from google.appengine.ext import webapp
from django import template

from auth.account import get_current_user, get_logout_url

import logging

def user_tpl(handler, template_data):
  user = get_current_user(handler.request)
  t = Template(template_data)

  vars = { 
    'user': user, 
  }
  if user:
    # TODO: logout should be javascript, need to mark logged out in session
    vars['logout'] = get_logout_url(handler.request, user)
  handler.response.out.write(t.render(vars))

def raw(parser, token):
    # Whatever is between {% raw %} and {% endraw %} will be preserved as
    # raw, unrendered template code.
    logging.info('parser = %r', parser)
    logging.info('token = %r', token)
    text = []
    parse_until = 'endraw'
    tag_mapping = {
        template.TOKEN_TEXT: ('', ''),
        template.TOKEN_VAR: ('{{', '}}'),
        template.TOKEN_BLOCK: ('{%', '%}'),
        template.TOKEN_COMMENT: ('{#', '#}'),
    }
    # By the time this template tag is called, the template system has already
    # lexed the template into tokens. Here, we loop over the tokens until
    # {% endraw %} and parse them to TextNodes. We have to add the start and
    # end bits (e.g. "{{" for variables) because those have already been
    # stripped off in a previous part of the template-parsing process.
    while parser.tokens:
        token = parser.next_token()
        if token.token_type == template.TOKEN_BLOCK and token.contents == parse_until:
            return template.TextNode(u''.join(text))
        start, end = tag_mapping[token.token_type]
        text.append(u'%s%s%s' % (start, token.contents, end))
    parser.unclosed_block_tag(parse_until)

register = webapp.template.create_template_register()
raw = register.tag(raw)
webapp.template.register_template_library('common.render')


