import asyncio
import base64
from copy import deepcopy
from datetime import datetime
from urllib.parse import unquote
from locale import setlocale, LC_TIME

from bs4 import BeautifulSoup
from bs4.element import Comment, Tag
from dateutil.relativedelta import relativedelta

from request import Session
from database import AttachedFile, DBManager, Post
from util import get_form_data_from_inputs


class SeoulSeoiCrawler:
    def __init__(self):
        asyncio.get_event_loop().run_until_complete(self.start_session())
        self.db_manager = DBManager()

    async def start_session(self):
        self.session = Session()
        await self.session.get('https://seo2.sen.es.kr/', allow_redirects=False)

    def __del__(self):
        del self.session
        del self.db_manager

    async def run(self):
        tasks = [
            self.crawl_board(
                'https://seo2.sen.es.kr/78584/subMenu.do', '공지사항'),
            self.crawl_board(
                'https://seo2.sen.es.kr/78585/subMenu.do', '가정통신문'),
            self.crawl_school_meal(),
        ]
        await asyncio.gather(*tasks)

    async def crawl_board(self, board_url, post_type_name):
        async def get_post_detail_view(form_data: dict):
            response = await self.session.post('https://seo2.sen.es.kr/dggb/module/board/selectBoardDetailAjax.do', data=form_data)
            await self.scrape_seoi_board_detail(response.text(), post_type_name, form_data['nttId'])

        form_data = {
            'bbsId': '',
            'bbsTyCode': '',
            'customRecordCountPerPage': '',
            'pageIndex': '',
        }
        response = await self.session.get(board_url)
        get_form_data_from_inputs(response.text(), form_data)
        # 리스트 한 페이지 당 게시글 수 조정
        form_data['customRecordCountPerPage'] = 1000

        tasks = []
        while True:
            response = await self.session.post('https://seo2.sen.es.kr/dggb/module/board/selectBoardListAjax.do', data=form_data)
            post_trs = BeautifulSoup(
                response.text(), 'html.parser').select('tbody > tr')
            for post_tr in post_trs:
                # 컬럼이 하나인 경우 조회된 내용 없음 -> 종료
                if len(post_tr.find_all('td')) == 1:
                    await asyncio.gather(*tasks)
                    return
                # 첫 페이지 제외 공지는 건너뛰도록
                if form_data['pageIndex'] != 1 and post_tr.td.span != None and post_tr.td.span.text == '공지':
                    continue
                form_data['nttId'] = post_tr.select_one('td > a').get('onclick').replace(
                    f"fnView('{form_data['bbsId']}', '", '').replace("');", '')
                form_data['ifNttId'] = base64.b64encode(
                    form_data['nttId'].encode('ascii')).decode('ascii')

                task = asyncio.create_task(
                    get_post_detail_view(deepcopy(form_data)))
                tasks.append(task)

            form_data['nttId'] = ''
            form_data['ifNttId'] = ''
            form_data['pageIndex'] = str(int(form_data['pageIndex']) + 1)

    async def scrape_seoi_board_detail(self, detail_page: str, post_type_name: str, ntt_id: str):
        soup = BeautifulSoup(detail_page, 'html.parser')
        elems_in_table = soup.select('tbody > tr > td > div')

        # content가 full html인 경우 및 html 주석 제거를 위해 필터링
        print(post_type_name, ntt_id, elems_in_table[1].text.strip())
        content_div = elems_in_table[3]
        content_list = content_div.p.contents if content_div.p.html == None else content_div.p.body.contents

        def stringify_tag_except_comments(tag: Tag):
            return str(tag) if not isinstance(tag, Comment) else ''
        content = ''.join(map(stringify_tag_except_comments, content_list))

        post = Post(
            school_name='서울서이초등학교',
            post_type_name=post_type_name,
            data_key=ntt_id,
            author=elems_in_table[0].text.strip(),
            upload_at=elems_in_table[1].text.strip(),
            title=elems_in_table[2].text.strip(),
            content=content,
        )

        # Get Attached Files
        file_div = soup.select_one('div#file_div')
        if file_div != None:
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
            atch_file_id = file_div.select_one(
                'input[name=atchFileId]').get('value')
            file_list_cnt = file_div.select_one(
                'input[name=fileListCnt]').get('value')

            file_list = []
            file_down_cnt = 0
            file_sn = -1
            while file_down_cnt < int(file_list_cnt):
                file_sn += 1
                file_url = f'https://seo2.sen.es.kr/dggb/board/boardFile/downFile.do?atchFileId={atch_file_id}&fileSn={str(file_sn)}'
                response = await self.session.get(file_url, headers={'User-Agent': user_agent})
                if 'Content-Disposition' not in response.headers:
                    continue

                file_list.append(AttachedFile(
                    data_key=f'{atch_file_id}-{file_sn}',
                    name=unquote(
                        response.headers['Content-Disposition'].split('filename=')[1]),
                    size=response.headers['Content-Length'],
                    download_url=file_url,  # 추후 업로드 경로 추가
                ))
                file_down_cnt += 1
            post.attached_files = file_list

        self.db_manager.store_post_data(post)

    async def crawl_school_meal(self):
        async def get_school_meal_popup_view(mlsvId):
            response = await self.session.post('https://seo2.sen.es.kr/dggb/module/mlsv/selectMlsvDetailPopup.do', data={'mlsvId': mlsvId})
            self.scrape_seoi_school_meal(response.text(), mlsvId)

        board_url = 'https://seo2.sen.es.kr/78586/subMenu.do'
        form_data = {
            'viewType': '',
            'pageIndex': '',
            'arrMlsvId': '',
            'srhMlsvYear': '',
            'srhMlsvMonth': '',
        }
        response = await self.session.get(board_url)
        get_form_data_from_inputs(response.text(), form_data)
        form_data['viewType'] = 'list'

        tasks = []
        date = datetime(2017, 1, 1)
        while True:
            if (date > datetime.now()):
                break
            form_data['srhMlsvYear'] = str(date.year)
            form_data['srhMlsvMonth'] = str(date.month).zfill(2)
            for page in ['1', '2']:
                form_data['pageIndex'] = page
                response = await self.session.post(board_url, data=form_data)
                menu_list_trs = BeautifulSoup(response.text(), 'html.parser').select(
                    'table.board_type01_tb_list > tbody > tr')
                for menu_list_tr in menu_list_trs:
                    tds = menu_list_tr.select('td')
                    if len(tds) <= 1:  # 조회된 데이터 없음
                        break
                    # 각 tr의 onclick 속성에서 mlsvId를 추출
                    mlsvId = tds[2].a.get('onclick').replace(
                        "fnDetail('", "").replace("');", "")

                    task = asyncio.create_task(
                        get_school_meal_popup_view(mlsvId))
                    tasks.append(task)

            date += relativedelta(months=1)
        await asyncio.gather(*tasks)

    def scrape_seoi_school_meal(self, popup_page: str, mlsvId):
        setlocale(LC_TIME, 'ko_KR.UTF-8')
        soup = BeautifulSoup(popup_page, 'html.parser')
        trs = soup.select('table.tbType02 > tbody > tr')

        type = trs[0].td.text.strip()
        date = datetime.strptime(trs[1].td.text.strip(), '%Y년 %m월 %d일 %A')
        menu = trs[3].td.text.strip()
        image_url = f"https://seo2.sen.es.kr{trs[5].td.img.get('src')}" if len(
            trs) == 6 else None
        if image_url == None:
            return

        # 내용(본문)은 메뉴, 식단이미지로 구성
        content = f'<p>{menu}</p>'
        content += f'<img src="{image_url}" alt="{date} {type} 급식 이미지" width="300">'

        post = Post(
            school_name='서울서이초등학교',
            post_type_name='급식 소식',
            data_key=mlsvId,
            author='서울서이초등학교',
            upload_at=date.strftime('%Y-%m-%d'),
            title=f'{date.strftime("%Y년 %m월 %d일")} [{type}]',
            content=content,
        )
        self.db_manager.store_post_data(post)
