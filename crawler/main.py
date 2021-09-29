import base64
from urllib.parse import unquote
from multiprocessing import Process
import requests
from bs4 import BeautifulSoup
import pymysql
from utils import my_get, my_post


def get_form_data_from_inputs(soup, form_data):
    inputs = soup.select('input[type=hidden]')
    for input in inputs:
        value = input.get('value')
        form_data[input.get('name')] = value if value != None else ''


def crawlBoard(board_url, post_type_id, db_connection):
    # Get Session
    cookies = dict(requests.get('https://seo2.sen.es.kr/',
                   allow_redirects=False).cookies)
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'

    form_data = {
        'bbsId': '',
        'bbsTyCode': '',
        'customRecordCountPerPage': '',
        'pageIndex': '',
    }
    get_form_data_from_inputs(BeautifulSoup(
        my_get(board_url, cookies=cookies).text, 'html.parser'), form_data)

    form_data['customRecordCountPerPage'] = 1000  # 리스트 한 페이지 당 게시글 수 조정
    while True:
        # Get Post List
        list_response = my_post(
            'https://seo2.sen.es.kr/dggb/module/board/selectBoardListAjax.do', cookies=cookies, data=form_data)
        soup = BeautifulSoup(list_response.text, 'html.parser')

        posts = soup.select('tbody > tr')
        for post in posts:
            if len(post.find_all('td')) == 1:
                return
            # 첫 페이지 제외 공지는 건너뛰도록
            if form_data['pageIndex'] != 1 and post.td.span != None and post.td.span.text == '공지':
                continue

            # Get Post Detail
            form_data['nttId'] = post.select_one('td > a').get('onclick').replace(
                f"fnView('{form_data['bbsId']}', '", '').replace("');", '')  # onclick 함수의 인자에서 nttId 값 추출
            form_data['ifNttId'] = base64.b64encode(
                form_data['nttId'].encode('ascii')).decode('ascii')
            post_response = my_post(
                'https://seo2.sen.es.kr/dggb/module/board/selectBoardDetailAjax.do', cookies=cookies, data=form_data)
            soup = BeautifulSoup(post_response.text, 'html.parser')

            elems_in_table = soup.select('tbody > tr > td > div')

            post_id = form_data['nttId']
            author = elems_in_table[0].text.strip()
            upload_at = elems_in_table[1].text.strip()
            title = db_connection.escape_string(elems_in_table[2].text.strip())
            content = db_connection.escape_string(
                str(elems_in_table[3]).lstrip('<div class="content">').rstrip('</div>'))
            print(f'{post_id} {author} {upload_at} {title}')

            # Insert Post or Update Post
            cursor = db_connection.cursor()
            cursor.execute(f"SELECT id FROM post WHERE id='{post_id}'")
            if cursor.fetchone() == None:
                cursor.execute(
                    f"INSERT INTO post (id, post_type_id, author, upload_at, title, content) VALUES ('{post_id}', '{post_type_id}', '{author}', '{upload_at}', '{title}', '{content}')")
            else:
                cursor.execute(
                    f"UPDATE post SET author='{author}', upload_at='{upload_at}', title='{title}', content='{content}' WHERE id='{post_id}'")
            db_connection.commit()

            # Get Attached Files
            file_div = soup.select_one('div#file_div')
            if file_div != None:
                atch_file_id = file_div.select_one(
                    'input[name=atchFileId]').get('value')
                file_list_cnt = file_div.select_one(
                    'input[name=fileListCnt]').get('value')

                file_down_cnt = 0
                file_sn = 0
                while file_down_cnt < int(file_list_cnt):
                    file_url = f'https://seo2.sen.es.kr/dggb/board/boardFile/downFile.do?atchFileId={atch_file_id}&fileSn={str(file_sn)}'
                    file_response = my_get(file_url, cookies, headers={
                        'User-Agent': user_agent})
                    if 'Content-Disposition' not in file_response.headers:
                        file_sn += 1
                        continue

                    file_down_cnt += 1
                    file_name = db_connection.escape_string(
                        unquote(file_response.headers['Content-Disposition'].split('filename=')[1]))
                    file_size = file_response.headers['Content-Length']

                    # Insert or Update File
                    cursor = db_connection.cursor()
                    cursor.execute(
                        f"SELECT id FROM attached_file WHERE attached_file_id='{atch_file_id}' AND file_sn='{file_sn}'")
                    if cursor.fetchone() == None:
                        cursor.execute(
                            f"INSERT INTO attached_file (post_id, attached_file_id, file_sn, name, size) VALUES ('{post_id}', '{atch_file_id}', '{file_sn}', '{file_name}', '{file_size}')")
                    else:
                        cursor.execute(
                            f"UPDATE attached_file SET name='{file_name}', size='{file_size}' WHERE attached_file_id='{atch_file_id}' AND file_sn='{file_sn}'")
                    db_connection.commit()

                    file_sn += 1

        form_data['nttId'] = ''
        form_data['ifNttId'] = ''
        form_data['pageIndex'] = str(int(form_data['pageIndex']) + 1)


def worker(board_url, postTypeName):
    db_connection = pymysql.connect(
        host='localhost', user='root', password='1234', db='elementary', charset='utf8')
    cursor = db_connection.cursor()
    cursor.execute(f"SELECT id FROM post_type WHERE name='{postTypeName}'")
    post_type_id = cursor.fetchone()[0]

    crawlBoard(board_url, post_type_id, db_connection)
    db_connection.close()


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
