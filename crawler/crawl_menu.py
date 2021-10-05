from datetime import datetime
from bs4.element import ResultSet, Tag
from dateutil.relativedelta import relativedelta
import requests
from bs4 import BeautifulSoup
import pymysql
from database import Post, store_post_data
from utils import get_form_data_from_inputs, my_get, my_post

def get_menu_list_trs(board_url: str, page: str, form_data: dict, cookies: dict) -> ResultSet[Tag]:
    """
    급식 메뉴 리스트 table의 tr 태그들을 반환

    Args:
        board_url: 급식 메뉴 게시판 url
        page: 페이지 번호
        form_data, cookies: 요청에 필요한 form data, cookie

    Returns:
        ResultSet[Tag]: 급식 메뉴 리스트 table의 tr 태그들
    """
    form_data['pageIndex'] = page
    response = my_post(board_url, cookies=cookies, data=form_data)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.select('table.board_type01_tb_list > tbody > tr')


def get_menu_data(mlsvId, post_type_id, cookies: dict) -> Post:
    """
    급식 메뉴 데이터 Post 객체를 반환

    Args:
        mlsvId: 급식 메뉴 데이터의 식별자 mlsvId
        post_type_id: 급식 메뉴 데이터의 게시글 타입 id
        cookies: 요청에 필요한 cookie
    
    Returns:
        Post: 급식 메뉴 데이터 Post 객체
    """

    response = my_post('https://seo2.sen.es.kr/dggb/module/mlsv/selectMlsvDetailPopup.do', cookies=cookies, data={'mlsvId': mlsvId})
    soup = BeautifulSoup(response.text, 'html.parser')

    trs = soup.select('table.tbType02 > tbody > tr')
    date = datetime.strptime(trs[1].td.text.strip(), '%Y년 %m월 %d일 %A').strftime('%Y-%m-%d')
    type = trs[0].td.text.strip()
    menu = trs[3].td.text.strip()
    image_url = f"https://seo2.sen.es.kr{trs[5].td.img.get('src')}" if len(trs) == 6 else None

    # 내용(본문)은 메뉴, 식단이미지로 구성
    content = f'<p>{menu}</p>'
    if image_url:
        content += f'<img src="{image_url}" alt="{date} {type} 급식 이미지" width="300">'

    return Post(
        post_type_id=post_type_id,
        data_key=f'mlsvId-{mlsvId}',
        author='관리자',
        upload_at=date,
        title=f'{date} [{type}]',
        content=content,
    )


def crawl_school_meal_menu(board_url: str, post_type_id, db_connection: pymysql.Connection):
    # Get Session
    cookies = dict(requests.get('https://seo2.sen.es.kr/', allow_redirects=False).cookies)
    form_data = {
        'viewType': '',
        'pageIndex': '',
        'arrMlsvId': '',
        'srhMlsvYear': '',
        'srhMlsvMonth': '',
    }
    get_form_data_from_inputs(my_get(board_url, cookies=cookies).text, form_data)
    form_data['viewType'] = 'list'

    date = datetime(2017, 1, 1)
    while True:
        if (date > datetime.now()):
            break
        form_data['srhMlsvYear'] = str(date.year)
        form_data['srhMlsvMonth'] = str(date.month).zfill(2)
        for page in ['1', '2']:
            menu_list = get_menu_list_trs(board_url, page, form_data, cookies)
            for menu_row in menu_list:
                tds = menu_row.select('td')
                if len(tds) <= 1:  # 조회된 데이터 없음
                    break
                # 각 tr의 onclick 속성에서 mlsvId를 추출
                mlsvId = tds[2].a.get('onclick').replace("fnDetail('", "").replace("');", "")
                menu_data = get_menu_data(mlsvId, post_type_id, cookies)
                store_post_data(db_connection, menu_data)
                print(menu_data.data_key, menu_data.title)

        date += relativedelta(months=1)
