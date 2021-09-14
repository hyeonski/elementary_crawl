import requests
from bs4 import BeautifulSoup
import base64
import time
import datetime
import sys
from urllib.parse import unquote


def myPost(url, cookies, data, headers=None):
    while True:
        response = requests.post(url, headers=headers, cookies=cookies, data=data)
        if response.status_code == 200:
            return response
        sys.stderr.write("[{timestamp}] Error: {code}\n".format(timestamp=datetime.datetime.now(), code=response.status_code))
        sys.stderr.flush()
        time.sleep(5)

# Get Session
response = requests.get('https://seo2.sen.es.kr/', allow_redirects=False)
cookies = dict(response.cookies)


# Get Notce
response = requests.get('https://seo2.sen.es.kr/78584/subMenu.do', cookies=cookies)
formData = {}

def getFormData(soup, formData):
    inputs = soup.select('input[type=hidden]')
    for input in inputs:
        value = input.get('value')
        formData[input.get('name')] = value if value != None else ''
getFormData(BeautifulSoup(response.text, 'html.parser'), formData)
formData['customRecordCountPerPage'] = 1000
while True:
    response = myPost('https://seo2.sen.es.kr/dggb/module/board/selectBoardListAjax.do', cookies=cookies, data=formData)
    soup = BeautifulSoup(response.text, 'html.parser')
    if soup.select_one('tbody > tr > td').text == '조회된 내용이 없습니다.':
        break

    posts = list(enumerate(soup.select('tbody > tr')))
    for index, post in posts:
        nttId = post.select_one('td > a').get('onclick').replace("fnView('BBSMSTR_000000012326', '", '').replace("');", '').replace("');", '')
        ifNttId = base64.b64encode(nttId.encode('ascii')).decode('ascii')
        formData['nttId'] = nttId
        formData['ifNttId'] = ifNttId
        response = myPost('https://seo2.sen.es.kr/dggb/module/board/selectBoardDetailAjax.do', cookies=cookies, data=formData)
        soup = BeautifulSoup(response.text, 'html.parser')

        list = soup.select('tbody > tr > td > div')

        author = list[0].text.strip()
        upload_at = list[1].text.strip()
        title = list[2].text.strip()
        content = list[3]

        fileDiv = soup.select_one('div#file_div')
        if fileDiv != None:
            atchFileId = fileDiv.select_one('input[name=atchFileId]').get('value')
            fileListCnt = fileDiv.select_one('input[name=fileListCnt]').get('value')

            for fileSn in range(int(fileListCnt)):
                fileResponse = requests.get('https://seo2.sen.es.kr/dggb/board/boardFile/downFile.do?atchFileId='+atchFileId+'&fileSn='+str(fileSn), headers={ 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36' })
                fileName = unquote(fileResponse.headers['Content-Disposition'].split('filename=')[1])
                fileSize = fileResponse.headers['Content-Length']
                print(fileName, fileSize)
    
    formData['nttId'] = ''
    formData['ifNttId'] = ''
    formData['pageIndex'] = str(int(formData['pageIndex']) + 1)
