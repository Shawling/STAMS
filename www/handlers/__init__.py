#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shawling'

' url handlers '

from apis import Page, APIValueError, APIResourceNotFoundError
from aiohttp import web
from config import configs
import logging

import markdown

logging.basicConfig(level=logging.WARNING)

def checkInt(value):
    p = 1
    try:
        p = int(value)
    except ValueError as e:
        raise APIValueError(value, '%s is not a int' % value)
    if p < 1:
        p = 1
    return p


def authManagerRequest(request):
    host = request.headers.get('X-Forwarded-For', None)
    if host is not None:
        if host != configs.admin_ip:
            logging.warning('403 API request from %s' % (host))
            return False
    return True


def text2html(text):
    lines = map(lambda s: '<p>%s</p>' % s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'), filter(lambda s: s.strip() != '', text.split('\n')))
    return ''.join(lines)


def text2markdown(text):
    return markdown.markdown(text, ['codehilite', 'fenced_code'])