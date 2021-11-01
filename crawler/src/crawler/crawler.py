from abc import ABCMeta, abstractmethod
import os
from uuid import uuid1

from bs4.element import Tag, Comment

from database import DBManager
from request import MySession
from upload_file import upload_image_from_bytes
from util import parse_base_url, print_log

class ACrawler(metaclass=ABCMeta):
    def __init__(self, school_name: str, school_main_url: str, num_of_sema: int=5):
        self.school_main_url = school_main_url
        self.school_base_url = parse_base_url(school_main_url)
        self.db_manager = DBManager()
        self.school = self.db_manager.get_school_by_name(school_name)
        self.num_of_sema = num_of_sema
        self.start_session(school_main_url)

    def start_session(self, school_main_url: str):
        self.session = MySession()
        self.session.get(school_main_url, allow_redirects=False)
        self.session.base_url = self.school_base_url

    def __del__(self):
        del self.session
        del self.db_manager

    def run(self):
        self.crawl_notice()
        self.crawl_parent_letter()
        self.crawl_school_meal_news()

    @abstractmethod
    def crawl_notice(self):
        pass

    @abstractmethod
    def crawl_parent_letter(self):
        pass

    @abstractmethod
    def crawl_school_meal_news(self):
        pass

    def upload_image_and_replace_src(self, img_tag: Tag):
        src = img_tag.get('src')
        try:
            extname = os.path.splitext(src)[1]
        except Exception:
            extname = ''

        try:
            if (not src.startswith('http')) and (self.session.base_url != None):
                src = self.session.base_url + src
            response = self.session.get(src)
            if response.status_code == 200:
                public_url = upload_image_from_bytes(response.content, f'{str(uuid1())}{extname}')
                img_tag['src'] = public_url
                img_tag['class'] = 'img-uploaded'
                if img_tag.get('style') != None:
                    del img_tag['style']
            else:
                raise Exception(f'{response.status_code}')
        except Exception as e:
            print_log(f'Error occured while getting image')
            img_tag['src'] = ''
    
    def manip_board_content(self, tag: Tag):
        for elem in tag.contents:
            if isinstance(elem, Tag):
                if elem.name == 'img':
                    self.upload_image_and_replace_src(elem)
                else:
                    self.manip_board_content(elem)
            if isinstance(elem, Comment):
                elem.extract()
