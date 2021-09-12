import requests
from bs4 import BeautifulSoup
import base64
import time
import datetime
import sys

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
        title = soup.select('tbody > tr > td > div')[2].text.strip()
        print(title)
    
    formData['nttId'] = ''
    formData['ifNttId'] = ''
    formData['pageIndex'] = str(int(formData['pageIndex']) + 1)
