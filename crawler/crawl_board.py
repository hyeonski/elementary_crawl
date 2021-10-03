import base64
from urllib.parse import unquote
from typing import List
import requests
from bs4.element import Comment, ResultSet, Tag
from bs4 import BeautifulSoup
import pymysql
from database import Post, AttachedFile, store_post_data, store_file_data
from utils import get_form_data_from_inputs, my_get, my_post


def get_post_list_trs(cookies: dict, form_data: dict) -> ResultSet[Tag]:
    list_response = my_post(
        'https://seo2.sen.es.kr/dggb/module/board/selectBoardListAjax.do',
        cookies=cookies,
        data=form_data)

    soup = BeautifulSoup(list_response.text, 'html.parser')
    return soup.select('tbody > tr')


def get_post_detail_soup(post: Tag, form_data: dict, cookies: dict) -> BeautifulSoup:
    # onclick 함수의 인자에서 nttId 값 추출
    form_data['nttId'] = post.select_one('td > a').get('onclick').replace(f"fnView('{form_data['bbsId']}', '", '').replace("');", '')
    form_data['ifNttId'] = base64.b64encode(form_data['nttId'].encode('ascii')).decode('ascii')
    post_response = my_post('https://seo2.sen.es.kr/dggb/module/board/selectBoardDetailAjax.do', cookies=cookies, data=form_data)
    return BeautifulSoup(post_response.text, 'html.parser')


def get_post_data(post_type_id, soup: BeautifulSoup, form_data: dict) -> Post:
    elems_in_table = soup.select('tbody > tr > td > div')

    content_div = elems_in_table[3]
    content_list = content_div.p.contents if content_div.p.html == None else content_div.p.body.contents

    def stringify_tag_except_comments(tag: Tag):
        return str(tag) if not isinstance(tag, Comment) else ''
    content = ''.join(map(stringify_tag_except_comments, content_list))

    return Post(
        post_type_id=post_type_id,
        data_key=f'nttId-{form_data["nttId"]}',
        author=elems_in_table[0].text.strip(),
        upload_at=elems_in_table[1].text.strip(),
        title=elems_in_table[2].text.strip(),
        content=content,
    )


def get_file_list(post_data_key, file_div: Tag, cookies: dict) -> List[AttachedFile]:
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'

    atch_file_id = file_div.select_one('input[name=atchFileId]').get('value')
    file_list_cnt = file_div.select_one('input[name=fileListCnt]').get('value')

    file_list: List[AttachedFile] = []

    file_down_cnt = 0
    file_sn = -1
    while file_down_cnt < int(file_list_cnt):
        file_sn += 1
        file_url = f'https://seo2.sen.es.kr/dggb/board/boardFile/downFile.do?atchFileId={atch_file_id}&fileSn={str(file_sn)}'
        file_response = my_get(file_url, cookies, headers={ 'User-Agent': user_agent })
        if 'Content-Disposition' not in file_response.headers:
            continue

        file_list.append(AttachedFile(
            post_data_key=post_data_key,
            attached_file_id=atch_file_id,
            file_sn=file_sn,
            name=unquote(file_response.headers['Content-Disposition'].split('filename=')[1]),
            size=file_response.headers['Content-Length'],
        ))
        file_down_cnt += 1
    return file_list


def crawl_board(board_url: str, post_type_id, db_connection: pymysql.Connection):
    # Get Session
    cookies = dict(requests.get('https://seo2.sen.es.kr/', allow_redirects=False).cookies)

    form_data = {
        'bbsId': '',
        'bbsTyCode': '',
        'customRecordCountPerPage': '',
        'pageIndex': '',
    }

    get_form_data_from_inputs(my_get(board_url, cookies=cookies).text, form_data)

    form_data['customRecordCountPerPage'] = 1000  # 리스트 한 페이지 당 게시글 수 조정
    while True:
        posts = get_post_list_trs(cookies, form_data)
        for post in posts:
            # 컬럼이 하나인 경우 조회된 내용 없음
            if len(post.find_all('td')) == 1:
                return
            # 첫 페이지 제외 공지는 건너뛰도록
            if form_data['pageIndex'] != 1 and post.td.span != None and post.td.span.text == '공지':
                continue

            soup = get_post_detail_soup(post, form_data, cookies)
            post_data = get_post_data(post_type_id, soup, form_data)
            store_post_data(db_connection, post_data)

            print(f'{post_data.data_key} {post_data.author} {post_data.upload_at} {post_data.title}')

            # Get Attached Files
            file_div = soup.select_one('div#file_div')
            if file_div != None:
                file_list = get_file_list(post_data.data_key, file_div, cookies)
                # 업데이트를 위해 이전 파일 목록 삭제
                cursor = db_connection.cursor()
                cursor.execute(f"DELETE FROM attached_file WHERE attached_file_id='{file_list[0].attached_file_id}'")
                for file in file_list:
                    store_file_data(db_connection, file)

        form_data['nttId'] = ''
        form_data['ifNttId'] = ''
        form_data['pageIndex'] = str(int(form_data['pageIndex']) + 1)