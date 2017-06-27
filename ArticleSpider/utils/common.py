#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/18 18:28
# @Author  : YangSen
# @Site    : 
# @File    : common.py
# @Software: PyCharm
import hashlib
import re


def get_md5(url):
    if isinstance(url,str):
        url=url.encode(encoding="utf-8")
    m=hashlib.md5()
    m.update(url)
    return  m.hexdigest()

def extract_num(text):
    #从字符串提取数字
    match_re=re.match(".*?(\d+).*",text)
    if match_re:
        nums=int(match_re.group(1))
    else:
        nums=0
    return nums


