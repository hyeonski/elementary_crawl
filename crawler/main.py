import requests
from bs4 import BeautifulSoup
import base64
import datetime
from urllib.parse import unquote
from multiprocessing import Process
from utils import myGet, myPost, printErrorEndl
import pymysql

PYMYSQL_DUPLICATE_ERROR = 1062


def getFormDataFromInputs(soup, formData):
    inputs = soup.select('input[type=hidden]')
    for input in inputs:
        value = input.get('value')
        formData[input.get('name')] = value if value != None else ''


def crawlBoard(boardUrl, postTypeId, dbConnection):
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

    formData['customRecordCountPerPage'] = 1000 # 리스트 한 페이지 당 게시글 수 조정
    while True:
        # Get Post List
        listResponse = myPost('https://seo2.sen.es.kr/dggb/module/board/selectBoardListAjax.do', cookies=cookies, data=formData)
        soup = BeautifulSoup(listResponse.text, 'html.parser')

        posts = soup.select('tbody > tr')
        for post in posts:
            if len(post.find_all('td')) == 1:
                return
            # 첫 페이지 제외 공지는 건너뛰도록
            if formData['pageIndex'] != 1 and post.td.span != None and post.td.span.text == '공지':
                continue

            # Get Post Detail
            formData['nttId'] = post.select_one('td > a').get('onclick').replace(f"fnView('{formData['bbsId']}', '", '').replace("');", '') # onclick 함수의 인자에서 nttId 값 추출
            formData['ifNttId'] = base64.b64encode(formData['nttId'].encode('ascii')).decode('ascii')
            postResponse = myPost('https://seo2.sen.es.kr/dggb/module/board/selectBoardDetailAjax.do', cookies=cookies, data=formData)
            soup = BeautifulSoup(postResponse.text, 'html.parser')

            elemsIntable = soup.select('tbody > tr > td > div')

            postId = formData['nttId']
            author = elemsIntable[0].text.strip()
            uploadAt = elemsIntable[1].text.strip()
            title = dbConnection.escape_string(elemsIntable[2].text.strip())
            content = dbConnection.escape_string(str(elemsIntable[3]).lstrip('<div class="content">').rstrip('</div>'))
            print(f'{postId} {author} {uploadAt} {title}')
            
            # Insert Post or Update Post
            cursor = dbConnection.cursor()
            cursor.execute(f"SELECT id FROM post WHERE id='{postId}'")
            if cursor.fetchone() == None:
                cursor.execute(f"INSERT INTO post (id, post_type_id, author, upload_at, title, content) VALUES ('{postId}', '{postTypeId}', '{author}', '{uploadAt}', '{title}', '{content}')")
            else:
                cursor.execute(f"UPDATE post SET author='{author}', upload_at='{uploadAt}', title='{title}', content='{content}' WHERE id='{postId}'")
            dbConnection.commit()

            # Get Attached Files
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
                    fileName = dbConnection.escape_string(unquote(fileResponse.headers['Content-Disposition'].split('filename=')[1]))
                    fileSize = fileResponse.headers['Content-Length']

                    # Insert or Update File
                    cursor = dbConnection.cursor()
                    cursor.execute(f"SELECT id FROM attached_file WHERE attached_file_id='{atchFileId}' AND file_sn='{fileSn}'")
                    if cursor.fetchone() == None:
                        cursor.execute(f"INSERT INTO attached_file (post_id, attached_file_id, file_sn, name, size) VALUES ('{postId}', '{atchFileId}', '{fileSn}', '{fileName}', '{fileSize}')")
                    else:
                        cursor.execute(f"UPDATE attached_file SET name='{fileName}', size='{fileSize}' WHERE attached_file_id='{atchFileId}' AND file_sn='{fileSn}'")
                    dbConnection.commit()

        formData['nttId'] = ''
        formData['ifNttId'] = ''
        formData['pageIndex'] = str(int(formData['pageIndex']) + 1)



def worker(boardUrl, postTypeName):
    dbConnection = pymysql.connect(host='localhost', user='root', password='1234', db='elementary', charset='utf8')
    cursor = dbConnection.cursor()
    cursor.execute(f"SELECT id FROM post_type WHERE name='{postTypeName}'")
    postTypeId = cursor.fetchone()[0]

    crawlBoard(boardUrl, postTypeId, dbConnection)
    dbConnection.close()


if __name__ == '__main__':
    p1 = Process(target=worker, args=(
        'https://seo2.sen.es.kr/78584/subMenu.do', 'notice'))
    p2 = Process(target=worker, args=(
        'https://seo2.sen.es.kr/78585/subMenu.do', 'parent_letter'))
    p3 = Process(target=worker, args=(
        'https://seo2.sen.es.kr/113876/subMenu.do', 'school_meal'))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()
