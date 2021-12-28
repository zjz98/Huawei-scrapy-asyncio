# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from MRCode.Config import Config
import os

class MrcodePipeline(object):
    def process_item(self, item, spider):
        file_path = Config.code_dir + os.sep + item['MR_ID'] + '.text'
        f = open(file_path, 'w')
        f.write(item['MR_code'])
        return item
