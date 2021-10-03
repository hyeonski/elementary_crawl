from datetime import datetime
from bs4.element import ResultSet, Tag
from dateutil.relativedelta import relativedelta
import requests
from bs4 import BeautifulSoup
import pymysql
from database import Post, store_post_data
from utils import get_form_data_from_inputs, my_get, my_post

def get_menu_list_trs(board_url: str, page: str, form_data: dict, cookies: dict) -> ResultSet[Tag]:
    form_data['pageIndex'] = page
    response = my_post(board_url, cookies=cookies, data=form_data)
    soup = BeautifulSoup(response.text, 'html.parser')
    return soup.select('table.board_type01_tb_list > tbody > tr')


def get_menu_data(mlsvId, post_type_id, cookies: dict) -> Post:
    response = my_post('https://seo2.sen.es.kr/dggb/module/mlsv/selectMlsvDetailPopup.do', cookies=cookies, data={'mlsvId': mlsvId})
    soup = BeautifulSoup(response.text, 'html.parser')

    trs = soup.select('table.tbType02 > tbody > tr')
    date = datetime.strptime(trs[1].td.text.strip(), '%Y년 %m월 %d일 %A').strftime('%Y-%m-%d')
    type = trs[0].td.text.strip()
    menu = trs[3].td.text.strip()
    image_url = f"https://seo2.sen.es.kr{trs[5].td.img.get('src')}" if len(trs) == 6 else None

    content = f'<p>{menu}</p>'
    if image_url:
        content += f'<img src="{image_url}" alt="{date} {type} 급식 이미지">'

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
                mlsvId = tds[2].a.get('onclick').replace("fnDetail('", "").replace("');", "")
                menu_data = get_menu_data(mlsvId, post_type_id, cookies)
                store_post_data(db_connection, menu_data)
                print(menu_data.data_key, menu_data.title)

        date += relativedelta(months=1)
