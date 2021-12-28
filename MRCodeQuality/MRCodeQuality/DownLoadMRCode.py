import time

import aiohttp
import asyncio
import json
import pymongo
from bs4 import BeautifulSoup
import os
from selenium import webdriver

from MRCodeQuality.Config import Config
from MRCodeQuality.GetMRIDList import GetMRIDList
from time import sleep
from pyppeteer import launch
from pyquery import PyQuery as pq


class MRcodedownload:

    # 某个项目的
    urllist = []

    def __init__(self):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.bro = webdriver.Chrome(Config.driver, chrome_options=option)

    # 获取所有MR的url
    def getallMRurl(self,projecturl):
        IDlist = GetMRIDList.getMergeRequestIidList(projecturl)
        for id in IDlist:
            self.urllist.append(projecturl + os.sep + '-' + os.sep+ 'merge_requests' + os.sep + id + os.sep + 'diffs')

    # 下载每个MRcode
    def downloadallcode(self, projecturl):
        self.getallMRurl(projecturl)
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        tasks = []
        for url in self.urllist:
            task = asyncio.ensure_future(self.download(url))
            tasks.append(task)
        loop.run_until_complete(asyncio.wait(tasks))


    # code为动态数据，使用selenium
    # 提前下载浏览器驱动程序http://chromedriver.storage.googleapis.com/index.html
    # 查看驱动程序和浏览器映射关系http://blog.csdn.net/huilan_same/articla/details/51896672
    async def download(self, url):
        if Config.proxy:
            proxy = await Config.getProxy()
            option = webdriver.ChromeOptions()
            option.add_argument('headless')
            option.add_argument('--proxy-server=%s' % proxy)
            bro = webdriver.Chrome('./chromedriver', chrome_options=option)
            try:
                bro.get(url)
                if(bro.find_element(url).is_displayed()):
                    print("proxy访问服务器成功，下载具体MR信息")
                    result = bro.page_source
                    print(result)
                else:
                    raise 0
            except Exception as e:
                print("当前proxy访问服务器失败，更换proxy重试")
                print(e)
                return await self.download(url)

        else:
            self.bro.get(url)
            sleep(2)
            result = self.bro.page_source

        code = self.parsecode(result)
        file_path = Config.CodePath + os.sep + url.split('/')[-2] + '.text'
        f = open(file_path, 'w')
        f.write(code)




    def parsecode(self, html):
        soup = BeautifulSoup(html, 'lxml')
        list = soup.find_all('div', class_="diff-td line_content with-coverage left-side new")
        s = ''
        for i in list:
            s = s + i.text
        return s


# test
if __name__ == '__main__':
    MRcodedownload().downloadallcode(Config.ProjectURL)


