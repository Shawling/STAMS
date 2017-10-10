#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shawling'
'''
async web application.
'''

import asyncio
import json
import logging
import os
import time
from datetime import datetime
import json
from aiohttp import web
import aiohttp
from jinja2 import Environment, FileSystemLoader
import requests
import orm
from config import configs
from coroweb import scan_handles_dir, add_static
from apis import APIPermissionError
from models import IP

logging.basicConfig(level=logging.WARNING)


def init_jinja2(app, **kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True))
    path = kw.get('path', None)
    if path is None:
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)
    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env


async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        return await handler(request)

    return logger


async def ip_factory(app, handler):
    async def ip_logger(request):
        host = request.headers.get('X-Forwarded-For', None)
        if host is not None:
            if request.path.startswith(
                    '/blog') or request.path == '/' or request.path.startswith(
                        '/gallery') or request.path.startswith('/archive'):
                ipSearchList = await IP.findAll('ip=?', [host])
                if len(ipSearchList) > 0:
                    ip = ipSearchList[0]
                    ip.last_time = time.time()
                    ip.access_count += 1
                    await ip.update()
                else:
                    url = '%s?ip=%s&token=%s' % (configs.ip138.url, host, configs.ip138.token)
                    async with aiohttp.ClientSession() as session:
                        async with session.get(url) as r:
                            retDic = json.loads(await r.text())
                            if retDic['ret'] == 'ok':
                                data = retDic['data']
                                country = data[0]
                                province = data[1]
                                city = data[2]
                                isp = data[3]
                                await IP(
                                    ip=host,
                                    country=country,
                                    province=province,
                                    city=city,
                                    isp=isp).save()
        return await handler(request)

    return ip_logger


async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            # 是否包含重定向方法
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(
                    r, ensure_ascii=False,
                    default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(
                    body=app['__templating__'].get_template(template).render(
                        **r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            # 返回Response Code
            return web.Response(status=r)
        # default:
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp

    return response


def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


async def init(loop):
    await orm.create_pool(loop=loop, **configs.db)
    app = web.Application(
        loop=loop, middlewares=[logger_factory, ip_factory, response_factory])
    init_jinja2(app, filters=dict(datetime=datetime_filter))
    scan_handles_dir(app,
                     os.path.join(
                         os.path.dirname(os.path.abspath(__file__)),
                         'handlers'))
    add_static(app,
               os.path.join(
                   os.path.dirname(os.path.abspath(__file__)), 'resources'),
               'resources')
    add_static(app, configs.pictures_path, 'pictures')
    srv = await loop.create_server(app.make_handler(), '127.0.0.1', 9000)
    logging.info('server started at http://127.0.0.1:9000...')
    return srv


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()