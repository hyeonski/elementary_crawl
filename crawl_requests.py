import requests
from bs4 import BeautifulSoup
import base64
import time
import datetime
import sys
from urllib.parse import unquote
from multiprocessing import Process
from sqlalchemy import create_engine

def printErrorEndl(error):
    sys.stderr.write(f"[{datetime.datetime.now()}] Error: {error}\n")
    sys.stderr.flush()

def myPost(url, cookies, data, headers=None):
    while True:
        try:
            response = requests.post(url, headers=headers, cookies=cookies, data=data)
            if response.status_code == 200:
                return response
            printErrorEndl(response.status_code)
            time.sleep(5)
        except Exception as e:
            printErrorEndl(e)
            time.sleep(10)

def myGet(url, cookies, headers=None):
    while True:
        try:
            response = requests.get(url, headers=headers, cookies=cookies)
            if response.status_code == 200:
                return response
            printErrorEndl(response.status_code)
            time.sleep(5)
        except Exception as e:
            printErrorEndl(e)
            time.sleep(10)

def getFormDataFromInputs(soup, formData):
    inputs = soup.select('input[type=hidden]')
    for input in inputs:
        value = input.get('value')
        formData[input.get('name')] = value if value != None else ''

def crawlBoard(boardUrl):
    # Get Session
    cookies = dict(requests.get('https://seo2.sen.es.kr/', allow_redirects=False).cookies)
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'


    count = 0
    formData = {
        'bbsId': '',
        'bbsTyCode': '',
        'customRecordCountPerPage': '',
        'pageIndex': '',
    }
    getFormDataFromInputs(BeautifulSoup(myGet(boardUrl, cookies=cookies).text, 'html.parser'), formData)

    formData['customRecordCountPerPage'] = 1000 # 한 페이지 당 게시글 수 조정
    while True:
        listResponse = myPost('https://seo2.sen.es.kr/dggb/module/board/selectBoardListAjax.do', cookies=cookies, data=formData)
        soup = BeautifulSoup(listResponse.text, 'html.parser')

        posts = soup.select('tbody > tr')
        for post in posts:
            if len(post.find_all('td')) == 1:
                return

            print(count)
            count += 1
            formData['nttId'] = post.select_one('td > a').get('onclick').replace(f"fnView('{formData['bbsId']}', '", '').replace("');", '') # onclick 함수의 인자에서 nttId 값 추출
            formData['ifNttId'] = base64.b64encode(formData['nttId'].encode('ascii')).decode('ascii')
            postResponse = myPost('https://seo2.sen.es.kr/dggb/module/board/selectBoardDetailAjax.do', cookies=cookies, data=formData)
            soup = BeautifulSoup(postResponse.text, 'html.parser')

            elemsIntable = soup.select('tbody > tr > td > div')

            author = elemsIntable[0].text.strip()
            upload_at = elemsIntable[1].text.strip()
            title = elemsIntable[2].text.strip()
            content = elemsIntable[3]
            print(author, upload_at, title)

            fileDiv = soup.select_one('div#file_div')
            if fileDiv != None:
                atchFileId = fileDiv.select_one('input[name=atchFileId]').get('value')
                fileListCnt = fileDiv.select_one('input[name=fileListCnt]').get('value')

                fileDownCnt = 0
                fileSn = 0
                while fileDownCnt < int(fileListCnt):
                    fileUrl = f'https://seo2.sen.es.kr/dggb/board/boardFile/downFile.do?atchFileId={atchFileId}&fileSn={str(fileSn)}'
                    fileResponse = myGet(fileUrl, cookies, headers={ 'User-Agent': userAgent })
                    fileSn += 1
                    if 'Content-Disposition' not in fileResponse.headers:
                        continue
                    fileDownCnt += 1
                    fileName = unquote(fileResponse.headers['Content-Disposition'].split('filename=')[1])
                    fileSize = fileResponse.headers['Content-Length']
                    print(fileName, fileSize)
            print("\n")

        formData['nttId'] = ''
        formData['ifNttId'] = ''
        formData['pageIndex'] = str(int(formData['pageIndex']) + 1)

if __name__ == '__main__':
    p1 = Process(target=crawlBoard, args=('https://seo2.sen.es.kr/78584/subMenu.do',))
    p2 = Process(target=crawlBoard, args=('https://seo2.sen.es.kr/78585/subMenu.do',))
    p3 = Process(target=crawlBoard, args=('https://seo2.sen.es.kr/113876/subMenu.do',))
    
    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
    # engine = create_engine('mysql://admin:12345678@elementary-crawl.c6pvxgc9cmjq.ap-northeast-2.rds.amazonaws.com/elementary')
