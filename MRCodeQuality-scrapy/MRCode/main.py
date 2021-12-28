# -*- coding: utf-8 -*-
__author__='pasaulis'
#在程序中运行命令行，方法调试，如：在jobbole.py中打个断点，运行就会停在那

from scrapy.cmdline import execute
import sys
import os
#
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# #测试目录获取是否正确
# print(os.path.dirname(os.path.abspath(__file__)))

#调用命令运行爬虫
execute(["scrapy","crawl","download"])