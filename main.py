#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/6/18 14:58
# @Author  : YangSen
# @Site    : 
# @File    : main.py
# @Software: PyCharm
from  scrapy.cmdline import execute

import sys
import os


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(["scrapy","crawl","jobbole"])
#execute(["scrapy", "crawl", "zhihu"])
#execute(["scrapy", "crawl", "lagou"])




# if __name__=="__main__":
#     remove_comment_tags()
