
import base64
from copy import deepcopy
from datetime import datetime
from typing import List
from urllib.parse import unquote
from locale import setlocale, LC_TIME
from uuid import uuid1

from bs4 import BeautifulSoup
from bs4.element import Tag
from dateutil.relativedelta import relativedelta
from crawler.crawler import ACrawler

from request import Response
from database import AttachedFile, Post, PostType
from upload_file import upload_attachment_from_bytes, upload_image_from_bytes
from util import get_form_data_from_inputs, stringify_tags


class SeoulSeoiCrawler(ACrawler):
    def crawl_notice(self):
        self.crawl_board('/78584/subMenu.do', '공지사항')

    def crawl_parent_letter(self):
        self.crawl_board('/78585/subMenu.do', '가정통신문')

    def crawl_school_meal_news(self):
        self.crawl_school_meal()

    def crawl_board(self, board_url: str, post_type_name: str):
        post_type = self.db_manager.get_post_type_by_name(post_type_name)
        form_data = {
            'bbsId': '',
            'bbsTyCode': '',
            'customRecordCountPerPage': '',
            'pageIndex': '',
        }
        response = self.session.get(board_url)
        get_form_data_from_inputs(response.text, form_data)
        # 리스트 한 페이지 당 게시글 수 조정
        form_data['customRecordCountPerPage'] = 1000

        while True:
            response = self.session.post('/dggb/module/board/selectBoardListAjax.do', data=form_data)
            post_trs = (BeautifulSoup(response.text, 'html.parser')
                        .select('tbody > tr'))
            for post_tr in post_trs:
                # 컬럼이 하나인 경우 조회된 내용 없음 -> 종료
                if len(post_tr.find_all('td')) == 1:
                    return
                # 첫 페이지 제외 공지는 건너뛰도록
                if form_data['pageIndex'] != 1 and post_tr.td.span != None and post_tr.td.span.text == '공지':
                    continue
                form_data['nttId'] = (post_tr.select_one('td > a').get('onclick')
                                      .replace(f"fnView('{form_data['bbsId']}', '", '')
                                      .replace("');", ''))
                form_data['ifNttId'] = (base64.b64encode(form_data['nttId'].encode('ascii'))
                                        .decode('ascii'))

                self.get_post_detail_view(deepcopy(form_data), post_type)

            form_data['nttId'] = ''
            form_data['ifNttId'] = ''
            form_data['pageIndex'] = str(int(form_data['pageIndex']) + 1)

    def get_post_detail_view(self, form_data: dict, post_type: PostType):
        response = self.session.post('/dggb/module/board/selectBoardDetailAjax.do', data=form_data)
        self.scrape_seoi_board_detail(response.text, post_type, form_data['nttId'])

    def scrape_seoi_board_detail(self, detail_page: str, post_type: PostType, ntt_id: str):
        soup = BeautifulSoup(detail_page, 'html.parser')
        elems_in_table = soup.select('tbody > tr > td > div')

        author = elems_in_table[0].text.strip()
        upload_at = elems_in_table[1].text.strip()
        title = elems_in_table[2].text.strip()
        content_div = elems_in_table[3]

        # content가 full html인 경우 및 html 주석 제거를 위해 필터링
        content = content_div.p if content_div.p.html == None else content_div.p.body
        self.manip_board_content(content)

        post = Post(
            school_id=self.school.id,
            post_type_id=post_type.id,
            data_key=ntt_id,
            author=author,
            upload_at=upload_at,
            title=title,
            content=stringify_tags(content.contents),
        )

        file_div = soup.select_one('div#file_div')
        if file_div != None:
            post.attached_files = self.get_attached_files(file_div)

        self.db_manager.save_post(post)

    def get_attached_files(self, file_div: Tag) -> List[AttachedFile]:
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36'
        atch_file_id = (file_div.select_one('input[name=atchFileId]')
                        .get('value'))
        file_list_cnt = (file_div.select_one('input[name=fileListCnt]')
                         .get('value'))

        dir_uuid = str(uuid1())
        file_list: List[AttachedFile] = []
        file_down_cnt = 0
        file_sn = -1
        while file_down_cnt < int(file_list_cnt):
            file_sn += 1
            response = self.session.get(
                '/dggb/board/boardFile/downFile.do',
                params={
                    'atchFileId': atch_file_id,
                    'fileSn': str(file_sn),
                },
                headers={'User-Agent': user_agent}
            )
            if 'Content-Disposition' not in response.headers:
                continue

            name = (unquote(response.headers['Content-Disposition']
                            .split('filename=')[1]))
            size = response.headers['Content-Length']
            public_url = upload_attachment_from_bytes(
                response.content, dir_uuid, name)

            file_list.append(AttachedFile(
                data_key=f'{atch_file_id}-{file_sn}',
                name=name,
                size=size,
                download_url=public_url,
            ))
            file_down_cnt += 1
        return file_list

    def crawl_school_meal(self):
        board_url = '/78586/subMenu.do'
        form_data = {
            'viewType': '',
            'pageIndex': '',
            'arrMlsvId': '',
            'srhMlsvYear': '',
            'srhMlsvMonth': '',
        }
        response = self.session.get(board_url)
        get_form_data_from_inputs(response.text, form_data)
        form_data['viewType'] = 'list'

        date = datetime(2017, 1, 1)
        while True:
            if (date > datetime.now()):
                break
            form_data['srhMlsvYear'] = str(date.year)
            form_data['srhMlsvMonth'] = str(date.month).zfill(2)
            for page in ['1', '2']:
                form_data['pageIndex'] = page
                response = self.session.post(board_url, data=form_data)
                menu_list_trs = (BeautifulSoup(response.text, 'html.parser')
                                 .select('table.board_type01_tb_list > tbody > tr'))
                for menu_list_tr in menu_list_trs:
                    tds = menu_list_tr.select('td')
                    if len(tds) <= 1:  # 조회된 데이터 없음
                        break
                    # 각 tr의 onclick 속성에서 mlsvId를 추출
                    mlsvId = (tds[2].a.get('onclick')
                              .replace("fnDetail('", "")
                              .replace("');", ""))

                    self.get_school_meal_popup_view(mlsvId)

            date += relativedelta(months=1)

    def get_school_meal_popup_view(self, mlsvId: str):
        response = self.session.post('/dggb/module/mlsv/selectMlsvDetailPopup.do', data={'mlsvId': mlsvId})
        self.scrape_seoi_school_meal(response.text, mlsvId)

    def scrape_seoi_school_meal(self, popup_page: str, mlsvId: str):
        setlocale(LC_TIME, 'ko_KR.UTF-8')
        soup = BeautifulSoup(popup_page, 'html.parser')
        trs = soup.select('table.tbType02 > tbody > tr')

        type = trs[0].td.text.strip()
        date = datetime.strptime(trs[1].td.text.strip(), '%Y년 %m월 %d일 %A')
        menu = trs[3].td.text.strip()
        image_url = f"https://seo2.sen.es.kr{trs[5].td.img.get('src')}" if len(trs) == 6 else None
        if image_url == None:
            return
        
        response = self.session.get(image_url)
        public_url = upload_image_from_bytes(response.content, str(uuid1()))
        # 내용(본문)은 메뉴, 식단이미지로 구성
        content = f'<p>{menu}</p>'
        content += f'<img src="{public_url}" alt="{date} {type} 급식 이미지" class="img-uploaded">'

        post = Post(
            school_id=self.school.id,
            post_type_id=self.db_manager.get_post_type_by_name('급식 소식').id,
            data_key=mlsvId,
            author='서울서이초등학교',
            upload_at=date.strftime('%Y-%m-%d'),
            title=f'{date.strftime("%Y년 %m월 %d일")} [{type}]',
            content=content,
        )
        self.db_manager.save_post(post)
