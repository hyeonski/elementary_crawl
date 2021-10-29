from abc import ABCMeta, abstractmethod
import asyncio
import os
from uuid import uuid1

from bs4.element import Tag, Comment
import requests

from database import DBManager
from request import Session
from upload_file import upload_image_from_bytes
from util import parse_base_url

class ACrawler(metaclass=ABCMeta):
    def __init__(self, school_name: str, school_main_url: str, num_of_sema: int=5):
        self.school_main_url = school_main_url
        self.school_base_url = parse_base_url(school_main_url)
        self.db_manager = DBManager()
        self.school = self.db_manager.get_school_by_name(school_name)
        self.num_of_sema = num_of_sema

    def __del__(self):
        del self.session
        del self.db_manager

    async def start_session(self, school_main_url: str):
        self.session = Session(self.num_of_sema)
        await self.session.get(school_main_url, allow_redirects=False)
        self.session.base_url = self.school_base_url

    async def run(self):
        await self.start_session(self.school_main_url)
        tasks = [
            self.crawl_notice(),
            self.crawl_parent_letter(),
            self.crawl_school_meal_news(),
        ]
        await asyncio.gather(*tasks)
        await self.session.close()

    @abstractmethod
    async def crawl_notice(self):
        pass

    @abstractmethod
    async def crawl_parent_letter(self):
        pass

    @abstractmethod
    async def crawl_school_meal_news(self):
        pass

    def upload_image_and_replace_src(self, img_tag: Tag):
        src = img_tag.get('src')
        try: extname = os.path.splitext(src)[1]
        except: extname = ''

        try:
            if (not src.startswith('http')) and (self.session.base_url != None):
                src = self.session.base_url + src
            response = requests.get(src)
            if response.status_code == 200:
                public_url = upload_image_from_bytes(response.content, f'{str(uuid1())}{extname}')
                img_tag['src'] = public_url
            else:
                print(f'[ERROR] {response.status_code} : {src}')
                raise Exception(f'{response.status_code}')
        except: img_tag['src'] = ''
    
    def manip_board_content(self, tag: Tag):
        for elem in tag.contents:
            if isinstance(elem, Tag):
                if elem.name == 'img':
                    self.upload_image_and_replace_src(elem)
                else:
                    self.manip_board_content(elem)
            if isinstance(elem, Comment):
                elem.extract()
