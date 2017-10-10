#!/usr/bin/env python3
# -*- coding: utf-8 -*-
'''
Models for user, blog, comment.
'''

__author__ = 'Shawling'

import time
import uuid

from orm import BooleanField, FloatField, Model, StringField, TextField, IntegerField


# 通过拼接时间戳与Python内置的uuid算法保证id的唯一性
def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class Blog(Model):
    __table__ = 'blogs'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    title = StringField(ddl='varchar(50)')
    summary = StringField(ddl='varchar(50)')
    content = TextField()
    picture = StringField(ddl='varchar(50)')
    created_at = FloatField(default=time.time)


class TagOfBlog(Model):
    __table__ = 'tag_of_blog'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    tag_id = StringField(ddl='varchar(50)')


class Tag(Model):
    __table__ = 'tags'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    name = StringField(ddl='varchar(50)')


class Pic(Model):
    __table__ = 'pictures'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    picture_path = StringField(ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    feel = StringField(default='', ddl='varchar(50)')
    created_at = FloatField(default=time.time)


class Comment(Model):
    __table__ = 'comments'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    blog_id = StringField(ddl='varchar(50)')
    user_name = StringField(ddl='varchar(50)')
    user_email = StringField(ddl='varchar(50)')
    user_website = StringField(ddl='varchar(50)')
    user_ip = StringField(ddl='varchar(50)')
    content = TextField()
    created_at = FloatField(default=time.time)


class IP(Model):
    __table__ = 'ips'

    id = StringField(primary_key=True, default=next_id, ddl='varchar(50)')
    ip = StringField(ddl='varchar(50)')
    country = StringField(ddl='varchar(50)')
    province = StringField(ddl='varchar(50)')
    city = StringField(ddl='varchar(50)')
    isp = StringField(ddl='varchar(50)')
    last_time = FloatField(default=time.time)
    access_count = IntegerField(default=1)