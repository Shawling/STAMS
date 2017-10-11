#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Shawling'
'''
用于压缩照片并自动上传到博客照片墙
使用时将py文件放在图片文件夹中执行
'''

import tinify
import os
import config_default
import requests

pictures_path = os.path.dirname(os.path.abspath(__file__))
tinypng_path = os.path.join(pictures_path, 'tinypng')
if not os.path.exists(tinypng_path):
    os.makedirs(tinypng_path)

tinify.key = config_default.configs['tinify_key']
for pic_file in os.listdir(pictures_path):
    pic_path = os.path.join(pictures_path, pic_file)
    if not os.path.isdir(pic_path):
        if pic_file[-3:] == 'jpg' or pic_file[-3:] == 'png' or pic_file[-4:] == 'jpeg' or pic_file[-3:] == 'JPG' or pic_file[-3:] == 'PNG' or pic_file[-4:] == 'JPEG':
            print('tinying %s' % pic_path)
            source = tinify.from_file(pic_path)
            source.to_file(os.path.join(tinypng_path, pic_file.lower()))

for pic_file in os.listdir(tinypng_path):
    pic_path = os.path.join(tinypng_path, pic_file)
    if not os.path.isdir(pic_path):
        if pic_file[-3:] == 'jpg' or pic_file[-3:] == 'png' or pic_file[-4:] == 'jpeg' or pic_file[-3:] == 'JPG' or pic_file[-3:] == 'PNG' or pic_file[-4:] == 'JPEG':
            url = 'http://www.shawling.cc/api/pics'
            files = {'pic': open(pic_path, 'rb')}
            print('uploading %s' % pic_path)
            response = requests.post(url, files=files)
            print(response.text)