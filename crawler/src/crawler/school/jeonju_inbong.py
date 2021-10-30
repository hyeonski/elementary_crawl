from typing import List
from urllib.parse import unquote
from datetime import datetime
from uuid import uuid1

from bs4 import BeautifulSoup
from bs4.element import ResultSet, Tag

from crawler.crawler import ACrawler
from database import AttachedFile, Post, PostType
from upload_file import upload_attachment_from_bytes
from util import stringify_tags


class JeonjuInbongCrawler(ACrawler):
    def crawl_notice(self):
        self.crawl_board('/inbong/M010501/list', '공지사항')

    def crawl_parent_letter(self):
        self.crawl_board('/inbong/M010701/list', '가정통신문')

    def crawl_school_meal_news(self):
        self.crawl_school_meal_photo()

    def crawl_board(self, board_url: str, post_type_name: str):
        post_type = self.db_manager.get_post_type_by_name(post_type_name)

        s_idx = 1
        while True:
            response = self.session.get(board_url, params={'s_idx': s_idx})
            soup = BeautifulSoup(response.text, 'html.parser')
            trs = soup.select('table.usm-brd-lst > tbody > tr')
            for tr in trs:
                tr_class = tr.get('class')
                if s_idx != 1 and tr_class != None and 'tch-ann' in tr_class:  # 공지는 첫 페이지만
                    continue
                post_detail_url = tr.select_one('td.tch-tit').select_one('a').get('href')
                self.crawl_board_detail_view(post_detail_url, post_type)
                last_index_tag = tr.select_one('td.tch-num')

            if last_index_tag == None or last_index_tag.text == '1':
                break
            s_idx += 1

    def crawl_board_detail_view(self, post_detail_url: str, post_type: PostType):
        response = self.session.get(post_detail_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        detail_table = soup.select_one('table#m_mainView')

        author = detail_table.select_one('td.tch-nme').text
        upload_at = detail_table.select_one('td.tch-dte').text
        upload_at = datetime.strptime(upload_at, '%y.%m.%d').strftime('%Y-%m-%d')
        title = detail_table.select_one('th.tch-tit').h5.text
        data_key = post_detail_url.split('?')[0].split('/')[-1]

        content_td = detail_table.select_one('td.tch-ctnt')
        self.manip_board_content(content_td)

        post = Post(
            school_id=self.school.id,
            post_type_id=post_type.id,
            data_key=data_key,
            author=author,
            upload_at=upload_at,
            title=title,
            content=stringify_tags(content_td.contents),
        )

        file_containers = detail_table.select('div.file-con')
        post.attached_files = self.get_attached_files(file_containers)
        self.db_manager.save_post(post)

    def get_attached_files(self, file_containers: ResultSet[Tag]) -> List[AttachedFile]:
        file_list: List[AttachedFile] = []
        dir_uuid = str(uuid1())

        for file_con in file_containers:
            file_url = file_con.select_one('a').get('href')
            response = self.session.get(file_url)
            name = unquote(response.headers['Content-Disposition'].split('filename=')[1]).strip('"')
            size = response.headers['Content-Length']
            data_key = file_url.split('/')[-1]
            public_url = upload_attachment_from_bytes(response.content, dir_uuid, name)

            file_list.append(AttachedFile(
                data_key=data_key,
                name=name,
                size=size,
                download_url=public_url,
            ))

        return file_list

    def crawl_school_meal_photo(self):
        post_type = self.db_manager.get_post_type_by_name('급식 소식')
        board_url = '/inbong/M01050604/list'

        s_idx = 1
        while True:
            response = self.session.get(board_url, params={'s_idx': s_idx})
            soup = BeautifulSoup(response.text, 'html.parser')
            album_list = soup.select_one('div.usm-album-lst > ul')
            items = album_list.select('li')
            if len(items) == 0:
                break

            for item in items:
                album_url = item.select_one('a').get('href')
                self.crawl_board_detail_view(album_url, post_type)

            s_idx += 1
