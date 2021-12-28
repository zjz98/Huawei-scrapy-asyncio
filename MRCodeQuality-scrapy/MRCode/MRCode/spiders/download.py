# -*- coding: utf-8 -*-
import scrapy
from selenium import webdriver
from MRCode.Config import Config
from MRCode.items import MrcodeItem
from bs4 import BeautifulSoup
import re


class DownloadSpider(scrapy.Spider):
    name = 'download'
    # allowed_domains = ['www.xxx.com']
    start_urls = [Config.ProjectURL + '/-/merge_requests?scope=all&state=opened']
    pageindex = 1
    Item_one_page = 20
    detail_urls = []  #在detail_url中的页面是动态加载数据，需要中间件处理的

    # 实例化selenium的浏览器对象
    def __init__(self):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        self.bro = webdriver.Chrome(executable_path = Config.driver,chrome_options=option)


    def parse(self, response):

        # 获取某一页的所有MRID和时间
        ID_onepage = []
        Time_onepage = []
        li_list = response.xpath('//*[@id="content-body"]/div[4]/ul/li')
        for li in li_list:
            MR_ID = li.xpath('./div/div[1]/div[2]/span[1]/text()').extract_first()
            MR_Time = li.xpath('./div/div[1]/div[2]/span[2]/time/@datetime').extract_first()
            MR_ID = MR_ID.strip('\n').strip('!')
            ID_onepage.append(MR_ID)
            Time_onepage.append(MR_Time)

            # 设置MR_ID值
            item = MrcodeItem()
            item['MR_ID'] = MR_ID

            #访问详情页,通过meta进行请求传参
            detail_url = Config.ProjectURL + '/-/merge_requests/' + str(MR_ID) + '/diffs'
            self.detail_urls.append(detail_url)
            yield scrapy.Request(url = detail_url,callback=self.parse_code, meta = {'item':item})


        # 如果该页数据达到最大值，则继续访问下一页
        if len(ID_onepage) >= self.Item_one_page:
            self.pageindex += 1
            new_url = Config.ProjectURL + '/-/merge_requests?scope=all&state=closed' + '&page=' + str(self.pageindex)
            yield scrapy.Request(url = new_url,callback=self.parse)

    def parse_code(self, response):

        soup = BeautifulSoup(response.text, 'lxml')
        list = soup.find_all('div', class_="diff-td line_content with-coverage left-side new")
        s = ''
        for i in list:
            s = s + i.text

        # 赋值给MR_code
        item = response.meta['item']
        item['MR_code'] = s

        #提交给管道
        yield item









