import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from MRCodeQuality.Config import Config
from datetime import datetime
import os

class GetMRIDList:
    # 一页里含有的mergeRequest的数量
    numberOfMergeRequestInOnePage = 20

    def __init__(self, pageIndex, timeTuple=()):
        self.pageIndex = pageIndex
        # 时间限制元组
        self.timeTuple = timeTuple
        # 判断是否应该停止爬取mergeRequest列表
        self.shouldFinish = False

    # 获取项目一页的MergeRequest的信息
    # 创建异步循环，并执行任务
    def getOnePageMergeRequestDataOfProject(self, mergeRequestIidList=[]):
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        loop = asyncio.get_event_loop()
        task = [asyncio.ensure_future(self.downloadInformation(mergeRequestIidList))]
        tasks = asyncio.gather(*task)
        loop.run_until_complete(tasks)


    # 下载数据
    async def downloadInformation(self, mergeRequestIidList=[]):
        async with aiohttp.ClientSession() as session:
            api = self.getOnePageMergeRequestApi()
            onepageIDList = await self.fetchData(session, api)
            if onepageIDList == None or len(onepageIDList) < self.numberOfMergeRequestInOnePage:
                self.shouldFinish = True
                print("获取MR_ID列表完成，最后pageIndex为：" + str(self.pageIndex))
            mergeRequestIidList.extend(onepageIDList)


    def getOnePageMergeRequestApi(self):

        api = Config.ProjectURL + os.sep + '-' + os.sep + 'merge_requests' + os.sep + '?scope=all&state=opened&page=' + str(self.pageIndex)
        return api


    # 对外暴露的接口，获取某个项目的符合时间限制的所有mergeRequestIid
    @staticmethod
    def getMergeRequestIidList(url='', timeLimit=()) -> []:
        pageIndex = 1
        mergeRequestIidList = []
        while True:
            helper = GetMRIDList(pageIndex, timeLimit)
            helper.getOnePageMergeRequestDataOfProject(mergeRequestIidList)
            if helper.shouldFinish:
                break
            pageIndex += 1
        return mergeRequestIidList


    # 异步获取数据，传入aiohttp.ClientSession和api
    # 获取proxy如果可以成功访问则return
    # 否则抛出异常重新执行该方法并选取proxy，直至访问成功
    async def fetchData(self, session, api):
        headers = Config.selectheaders()
        proxy = None
        if Config.proxy:
            proxy = await Config.getProxy()
        try:
            async with session.get(api, ssl=False, proxy=proxy
                    , headers=headers) as response:
                print("response status: ", response.status)
                if response.status == 403:
                    raise 403
                if response.status == 401:
                    raise 401
                # 在这里注意！使用response.json()有问题！！
                print("proxy访问服务器成功，下载该页码所有MR_ID")
                result = await response.text()
                return await self.parseToIDList(result)
        except Exception as e:
            print("当前proxy访问服务器失败，更换proxy重试")
            print(e)
            return await self.fetchData(session, api)

    # 解析html，提取某一页符合时间要求的ID列表
    async def parseToIDList(self, html) -> []:
        soup = BeautifulSoup(html, 'lxml')
        preIDlist = soup.find_all('span', class_='issuable-reference')
        IDList = []
        for i in preIDlist:
            IDList.append((i.text).strip()[1:])

        #提取每个MR时间信息
        TimeList = []
        ex = '<time class="js-timeago".*?datetime="(.*?)" data.*?</time>'
        preTimeList = re.findall(ex, html, re.S)
        for i in preTimeList:
            TimeList.append(i.split('T')[0])

        result = []
        # 选择符合时间要求的ID
        for i in range(0, len(TimeList)):
            date = datetime.strptime(TimeList[i],'%Y-%m-%d')
            datestart = datetime.strptime(Config.StartTime, '%Y-%m-%d')
            dateend = datetime.strptime(Config.EndTime, '%Y-%m-%d')
            if (date >= datestart)  & (date <= dateend):
                result.append(IDList[i])

        return result

    
# test
if __name__ == '__main__':
    arr = GetMRIDList.getMergeRequestIidList(Config.ProjectURL)
    print(arr)