#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shawling'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio
from PIL import Image
from aiohttp import web
import os
from coroweb import get, post
from apis import Page, APIValueError, APIResourceNotFoundError, APIPermissionError
from models import Blog, TagOfBlog, Tag, next_id, Pic, Comment
from config import configs
from handlers import authManagerRequest


@post('/api/blogs')
async def api_creat_blog(request,
                         *,
                         title,
                         summary,
                         content,
                         tag_str,
                         picture=None):
    if not authManagerRequest(request):
        raise APIPermissionError('不要乱来哦！不然我拿小拳拳。。。')
    if not title or not title.strip():
        raise APIValueError('title', 'title cannot be empty.')
    if not content or not content.strip():
        raise APIValueError('content', 'content cannot be empty.')
    if not tag_str or not tag_str.strip():
        raise APIValueError('tag_str', 'tag_str cannot be empty.')

    blogID = next_id()
    blog = Blog(
        id=blogID,
        title=title.strip(),
        summary=summary.strip(),
        content=content.strip(),
        picture=picture)
    await blog.save()

    tagNameList = tag_str.split(',')
    for tagName in tagNameList:
        tagFetchList = (await Tag.findAll('name=?', [tagName]))
        if len(tagFetchList) < 1:
            tag = Tag(name=tagName)
            await tag.save()
        else:
            tag = tagFetchList[0]
        await TagOfBlog(blog_id=blogID, tag_id=tag.id).save()
    return blog


@post('/api/pics')
async def api_upload_pic(request):
    if not authManagerRequest(request):
        raise APIPermissionError('不要乱来哦！不然我拿小拳拳。。。')
    reader = await request.multipart()
    pic = await reader.next()
    filename = next_id() + '.' + pic.filename.split('.')[-1]
    size = 0
    picPath = os.path.join(configs.pictures_path, filename)
    with open(picPath, 'wb') as f:
        while True:
            chunk = await pic.read_chunk()  # 8192 bytes by default.
            if not chunk:
                break
            size += len(chunk)
            f.write(chunk)

    picID = next_id()
    mysqlPicPath = '/pictures/' + filename
    pic = Pic(id=picID, picture_path=mysqlPicPath)
    await pic.save()

    return web.Response(text='{}' ''.format(picID))


@post('/api/blogs/{id}/comments')
async def api_create_comment(id, request, *, name, email, website, content):
    if not name or not name.strip():
        raise APIValueError('name')
    if not content or not content.strip():
        raise APIValueError('content')
    blog = await Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    peername = request.transport.get_extra_info('peername')
    ip = peername[0]
    comment = Comment(
        blog_id=blog.id,
        user_name=name.strip(),
        user_email=email.strip(),
        user_website=website.strip(),
        user_ip=ip,
        content=content.strip())
    await comment.save()
    return comment