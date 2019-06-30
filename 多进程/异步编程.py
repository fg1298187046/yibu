import asyncio
from aiohttp import ClientSession
import requests
import json

import re,pymysql

import openpyxl


workspace=openpyxl.load_workbook('AQY.xlsx')
async def parse_url(url):
     async with ClientSession() as sesssion:
         async with sesssion.get(url) as response:
             response=await response.text()
             return response


async def parse_playurl(name,score,content,main_charactor):
        tx_id=re.findall(r'"tvId":(\d{0,20})',content)[0]
        api='https://pcw-api.iqiyi.com/video/video/hotplaytimes/'+str(tx_id)
        api2='https://iface2.iqiyi.com/like/count?businessType=14&entityId=%s&qc5=b7abd25636fdbccec1035ade486d536b&qyid=b7abd25636fdbccec1035ade486d536b&callback=jsonp_1560695467937_2693'%tx_id
        hot_json=await parse_url(api)
        collection_json=await parse_url(api2)
        hot=re.search(r'"hot":(\d{0,5})',hot_json).group(1)
        collection=int(re.search(r'"data":"(\w+?)"',collection_json).group(1))

        await save_excel(name,score,hot,main_charactor,collection)

async def save_excel(name,scoce,hot,main,collection):
    workspace.guess_types=True
    wb=workspace.get_sheet_by_name('Sheet1')
    wb.append([name,scoce,hot,main,collection])
    print(name,scoce,hot,main,collection)
    workspace.save('AQY.xlsx')



# async def async_mysql():
#     dbparams = {
#         'host': 'localhost',
#         'user': 'root',
#         'password': 'fengge520',
#         'db': 'sqltest',
#         'charset': 'utf8',
#         'cursorclass': DictCursor}
#     conn= adbapi.ConnectionPool('pymysql', **dbparams)
#     qure=conn.runInteraction()

async def analyze_json(url):
        text=await parse_url(url)
        json_nm=json.loads(text)
        data=json_nm['data']
        List=data['list']

        for each in List:
            main_charactor ='暂无'
            name=each['name']
            score=each['score']
            palyurl=each['playUrl']
            try:
                main_charactor=each['secondInfo'].split(':')[-1]
            except:
                pass
            content=await parse_url(palyurl)
            await parse_playurl(name,score,content,main_charactor)


def main():
        url='http://pcw-api.iqiyi.com/search/video/videolists?access_play_control_platform=14&channel_id=1&data_type=1&from=pcw_list&is_album_finished=&is_purchase=&key=&market_release_date_level=&mode=8&pageNum=%d&pageSize=48&site=iqiyi&source_type=&three_category_id=&without_qipu=1'
        taskss=[asyncio.ensure_future(analyze_json(url%x)) for x in range(1,100)]
        loop.run_until_complete(asyncio.wait(taskss))
         # asyncio.ensure_future(analyze_json(tasks))





if __name__ == '__main__':
    loop=asyncio.get_event_loop()
    main()

