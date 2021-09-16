from database import AttachedFile, Post, PostType
import requests
from bs4 import BeautifulSoup
import base64
import time
import datetime
import sys
from urllib.parse import unquote
from multiprocessing import Process
from database import Post
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from pymysql.err import IntegrityError

PYMYSQL_DUPLICATE_ERROR = 1062

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

def crawlBoard(boardUrl, postTypeId, dbSession):
    # Get Session
    cookies = dict(requests.get('https://seo2.sen.es.kr/', allow_redirects=False).cookies)
    userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'

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
            if formData['pageIndex'] != 1 and post.td.span != None and post.td.span.text == '공지':
                continue


            formData['nttId'] = post.select_one('td > a').get('onclick').replace(f"fnView('{formData['bbsId']}', '", '').replace("');", '') # onclick 함수의 인자에서 nttId 값 추출
            formData['ifNttId'] = base64.b64encode(formData['nttId'].encode('ascii')).decode('ascii')
            postResponse = myPost('https://seo2.sen.es.kr/dggb/module/board/selectBoardDetailAjax.do', cookies=cookies, data=formData)
            soup = BeautifulSoup(postResponse.text, 'html.parser')

            elemsIntable = soup.select('tbody > tr > td > div')

            post = Post(
                id=int(formData['nttId']),
                type=postTypeId,
                author=elemsIntable[0].text.strip(),
                upload_at=datetime.datetime.strptime(elemsIntable[1].text.strip(), '%Y-%m-%d'),
                title=elemsIntable[2].text.strip(),
                content=str(elemsIntable[3])
                )

            attachedFiles = []
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
                    attachedFiles.append(AttachedFile(
                        post=post.id,
                        attachedFileId=atchFileId,
                        fileSn=fileSn,
                        name=fileName,
                        size=fileSize,
                        downloadUrl=fileUrl,
                        previewUrl=f'http://viewhosting.ssem.or.kr:8080/SynapDocViewServer/job?fid={atchFileId}_{fileSn}&filePath=https://seo2.sen.es.kr:443/dggb/cnvrFileDown.do?atchFileId={atchFileId}:{fileSn}&convertType=0&fileType=URL&sync=true'
                    ))
            post.attachedFiles = attachedFiles
            #####
            try:
                dbSession.add(post)
                dbSession.commit()
            except IntegrityError as e:
                printErrorEndl(f'[{datetime.datetime.now()}] d{e.args[0]}d')
                if e.args[0] != PYMYSQL_DUPLICATE_ERROR:
                    raise e
            #####

        formData['nttId'] = ''
        formData['ifNttId'] = ''
        formData['pageIndex'] = str(int(formData['pageIndex']) + 1)

def worker(boardUrl, postTypeName):
    engine = create_engine('mysql+pymysql://admin:12345678@elementary-crawl.c6pvxgc9cmjq.ap-northeast-2.rds.amazonaws.com/elementary')
    dbSession = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
    postType = dbSession.query(PostType).filter(PostType.name == postTypeName).one()
    crawlBoard(boardUrl, postType.id, dbSession)


if __name__ == '__main__':
    # p1 = Process(target=crawlBoard, args=('https://seo2.sen.es.kr/78584/subMenu.do',))
    # p2 = Process(target=crawlBoard, args=('https://seo2.sen.es.kr/78585/subMenu.do',))
    p3 = Process(target=worker, args=('https://seo2.sen.es.kr/113876/subMenu.do', 'school_meal'))
    
    # p1.start()
    # p2.start()
    p3.start()

    # p1.join()
    # p2.join()
    p3.join()
    
