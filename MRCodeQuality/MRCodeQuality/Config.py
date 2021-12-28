# _*_ coding: utf-8 _*_
import random
import configparser
from MRCodeQuality.ProxyHelper import ProxyHelper
import re

class Config:

    # 项目URL
    ProjectURL = 'https://gitlab.com/spacecowboy/Feeder'

    # 选择时间
    StartTime = '2021-06-01'
    EndTime = '2021-09-01'

    # 存储代码的路径
    CodePath = '/Users/juzhengzhang/Desktop/华为三期/code/HuaweiProjectIII/MRCodeQuality/MRCode'

    # 浏览器驱动路径
    driver = '/Users/juzhengzhang/Desktop/华为三期/code/HuaweiProjectIII/MRCodeQuality/chromedriver'
    
    # 是否启用代理
    proxy = False


    USER_AGENTS = [
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
        "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
        "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
        "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
        "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
    ]

    @staticmethod
    def selectheaders():
        ch = random.choice(Config.USER_AGENTS)
        header = {'User-Agent': ch}
        return header



    # 使用代理
    
    @staticmethod
    async def getProxy():
        """获取代理ip池中的ip  详细看 ProxyHelper"""
        proxy = await ProxyHelper.getAsyncSingleProxy()
        if proxy is not None:
            return 'http://{}'.format(proxy)
        return None

    