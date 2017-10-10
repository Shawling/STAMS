#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shawling'

' url handlers '

import re, time, json, logging, hashlib, base64, asyncio

from aiohttp import web
import os

from coroweb import get, post

from apis import Page, APIValueError, APIResourceNotFoundError, APIPermissionError

from models import Blog, TagOfBlog, Tag, next_id, Pic, Comment
from config import configs
from handlers import checkInt

import time
from datetime import datetime

from handlers import authManagerRequest, text2html, text2markdown


@get('/')
async def index():
    return await get_blog_page()


@get('/blogs/pageindex/{page}')
async def get_page(page='1'):
    return await get_blog_page(page)


async def get_blog_page(page='1'):
    num = await Blog.findNumber('count(id)')
    if num == 0:
        blogs = []
    else:
        blogs = await Blog.findAll(orderBy='created_at desc')
    for blog in blogs:
        blog.html_summary = text2markdown(blog.summary)
        pic = await Pic.find(blog.picture)
        if pic is not None:
            blog.picture = pic.picture_path
        tags_of_blog = await TagOfBlog.findAll('blog_id=?', [blog.id])
        blog.tags = []
        for tag_of_blog in tags_of_blog:
            tag = await Tag.find(tag_of_blog.tag_id)
            blog.tags.append(tag)
    tags = await Tag.findAll()
    p = Page(len(blogs), checkInt(page))
    return {
        '__template__': 'index.html',
        'blogs': blogs[p.offset:p.offset + p.limit],
        'tags': tags,
        'page': p,
        '__navi_1_active__': 'am-active'
    }


@get('/blogs/filter/tag')
async def get_blogs_by_tag_and_page(*, tagID, page='1'):
    return await get_blogs_by_tag_and_page_util(tagID, page)


async def get_blogs_by_tag_and_page_util(tagID, page='1'):
    tag_of_blogs = await TagOfBlog.findAll('tag_id=?', tagID)
    blogs = []
    for tag_of_blog in tag_of_blogs:
        blogs.append(await Blog.find(tag_of_blog.blog_id))
    blogs.sort(key=lambda x: x.created_at, reverse=True)
    for blog in blogs:
        blog.html_summary = text2markdown(blog.summary)
        pic = await Pic.find(blog.picture)
        if pic is not None:
            blog.picture = pic.picture_path
        tags_of_blog = await TagOfBlog.findAll('blog_id=?', [blog.id])
        blog.tags = []
        for tag_of_blog in tags_of_blog:
            tag = await Tag.find(tag_of_blog.tag_id)
            blog.tags.append(tag)
    tags = await Tag.findAll()
    p = Page(len(blogs), checkInt(page))
    return {
        '__template__':
        'searchlist.html',
        'blogs':
        blogs[p.offset:p.offset + p.limit],
        'tags':
        tags,
        'page':
        p,
        '__navi_1_active__':
        'am-active',
        'page_pre_action':
        '/blogs/filter/tag?tagID=%s&page=%s' % (tagID, p.page_index - 1),
        'page_next_action':
        '/blogs/filter/tag?tagID=%s&page=%s' % (tagID, p.page_index + 1)
    }


@get('/blogs/filter/searchString')
async def get_blogs_by_searchString_and_page(*, searchstring, page='1'):
    return await get_blogs_by_searchString_and_page_util(searchstring, page)


async def get_blogs_by_searchString_and_page_util(searchstring, page='1'):
    blogs = await Blog.findAll(
        '`title` like ? or `content` like ?',
        ['%%%s%%' % (searchstring),
         '%%%s%%' % (searchstring)],
        orderBy='created_at desc')
    for blog in blogs:
        blog.html_summary = text2markdown(blog.summary)
        pic = await Pic.find(blog.picture)
        if pic is not None:
            blog.picture = pic.picture_path
        tags_of_blog = await TagOfBlog.findAll('blog_id=?', [blog.id])
        blog.tags = []
        for tag_of_blog in tags_of_blog:
            tag = await Tag.find(tag_of_blog.tag_id)
            blog.tags.append(tag)
    tags = await Tag.findAll()
    p = Page(len(blogs), checkInt(page))
    return {
        '__template__':
        'searchlist.html',
        'blogs':
        blogs[p.offset:p.offset + p.limit],
        'tags':
        tags,
        'page':
        p,
        '__navi_1_active__':
        'am-active',
        'page_pre_action':
        '/blogs/filter/searchString?searchstring=%s&page=%s' %
        (searchstring, p.page_index - 1),
        'page_next_action':
        '/blogs/filter/searchString?searchstring=%s&page=%s' %
        (searchstring, p.page_index + 1)
    }


@get('/blog/{id}')
async def get_blog(id):
    blog = await Blog.find(id)
    if blog is None:
        raise APIResourceNotFoundError('Blog')
    blog.html_content = text2markdown(blog.content)
    pic = await Pic.find(blog.picture)
    if pic is not None:
        blog.picture = pic.picture_path

    tags_of_blog = await TagOfBlog.findAll('blog_id=?', [blog.id])
    blog.tags = []
    for tag_of_blog in tags_of_blog:
        tag = await Tag.find(tag_of_blog.tag_id)
        blog.tags.append(tag)

    comments = await Comment.findAll(
        'blog_id=?', [id], orderBy='created_at desc')
    for c in comments:
        c.html_content = text2html(c.content)

    prevBlogs = await Blog.findAll(
        '`created_at`<?', [blog.created_at],
        orderBy='created_at desc',
        limit=1)
    nextBlogs = await Blog.findAll(
        '`created_at`>?', [blog.created_at], orderBy='created_at asc', limit=1)
    prevBlog = None
    nextBlog = None
    if len(prevBlogs) >= 1:
        prevBlog = prevBlogs[0].id
    if len(nextBlogs) >= 1:
        nextBlog = nextBlogs[0].id
    return {
        '__template__': 'blog.html',
        'blog': blog,
        'comments': comments,
        'prevBlog': prevBlog,
        'nextBlog': nextBlog
    }


@get('/gallery')
async def page_gallery():
    num = await Pic.findNumber('count(id)')
    if num == 0:
        pics = []
    else:
        pics = await Pic.findAll(orderBy='created_at desc')

    pics_not_found = []
    pics_founded = []
    for pic in pics:
        picFile = os.path.join(
            os.path.abspath(os.path.join(os.path.dirname(__file__), "..")),
            pic.picture_path[1:])
        if not os.path.exists(picFile):
            pics_not_found.append(pic)
        else:
            pics_founded.append(pic)

    return {
        '__template__': 'gallery.html',
        'picList': pics_founded,
        '__navi_2_active__': 'am-active'
    }


@get('/archive')
async def page_archive():
    num = await Blog.findNumber('count(id)')
    if num == 0:
        blogs = []
    else:
        blogs = await Blog.findAll(orderBy='created_at desc')

    for blog in blogs:
        tags_of_blog = await TagOfBlog.findAll('blog_id=?', [blog.id])
        blog.tags = []
        for tag_of_blog in tags_of_blog:
            tag = await Tag.find(tag_of_blog.tag_id)
            blog.tags.append(tag)

    dates = {}
    for blog in blogs:
        dt = datetime.fromtimestamp(blog.created_at)
        blog.year = dt.year
        blog.month = dt.month
        blog.day = dt.day
        if dates.get(dt.year, None) is None:
            dates[dt.year] = {}
        if dates[dt.year].get(dt.month, None) is None:
            dates[dt.year][dt.month] = []
        dates[dt.year][dt.month].append(blog)

    return {
        '__template__': 'archive.html',
        'dates': dates,
        '__navi_3_active__': 'am-active'
    }


@get('/tibbie')
async def managerCreatBlogsPages(request):
    if not authManagerRequest(request):
        raise APIPermissionError('不要乱来哦！不然我拿小拳拳。。。')
    tags = await Tag.findAll()
    return {'__template__': 'manager_blog_edit.html', 'tags': tags}
