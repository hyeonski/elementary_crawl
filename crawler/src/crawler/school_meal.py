from typing import Tuple
import os
from datetime import datetime

from bs4 import BeautifulSoup

from request import Session
from database import DBManager, Post, School


class SchoolMealCrawler:
    def __init__(self):
        self.key = os.environ['NEIS_OPEN_API_KEY']
        self.db_manager = DBManager()
        self.session = Session()

    def __del__(self):
        del self.db_manager

    def run(self):
        school_list = self.db_manager.get_all_schools()
        for school in school_list:
            self.crawl_school_meal(school)

    def crawl_school_meal(self, school: School):
        now = datetime.now()
        ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE = self.get_school_code(school.name)
        pSize = 1000
        pIndex = 1
        response = self.session.get('https://open.neis.go.kr/hub/mealServiceDietInfo', params={
            'key': self.key,
            'Type': 'xml',
            'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE,
            'SD_SCHUL_CODE': SD_SCHUL_CODE,
            'pSize': pSize,
            'pIndex': pIndex,
            'MLSV_FROM_YMD': datetime(now.year, now.month, 1).strftime('%Y%m%d'),
        })
        soup = BeautifulSoup(response.text, 'xml')
        code = soup.select_one('RESULT > CODE').text
        if code == 'INFO-200':
            return
        if code != 'INFO-000':
            raise Exception(f'급식 메뉴 크롤링 중 알 수 없는 오류 발생: {code}')

        for item in soup.select('row'):
            meal_type = item.select_one('MMEAL_SC_NM').text
            date = datetime.strptime(
                item.select_one('MLSV_YMD').text,
                '%Y%m%d',
            )
            menu = item.select_one('DDISH_NM').text
            self.db_manager.save_post(Post(
                school_id=school.id,
                post_type_id=self.db_manager.get_post_type_by_name('오늘의 급식').id,
                data_key=date.strftime('%Y%m%d'),
                author=school.name,
                upload_at=date.strftime('%Y-%m-%d'),
                title=f'{date.strftime("%Y년 %m월 %d일")} [{meal_type}]',
                content=f'<p>{menu}</p>',
            ))

    def get_school_code(self, school_name: str) -> Tuple[str, str]:
        response = self.session.get('https://open.neis.go.kr/hub/schoolInfo', params={
            'key': self.key,
            'Type': 'xml',
            'SCHUL_NM': school_name
        })
        soup = BeautifulSoup(response.text, 'xml')
        if soup.select_one('RESULT > CODE').text != 'INFO-000':
            raise Exception(
                f'해당하는 학교 정보가 없습니다.: {soup.select_one("RESULT > CODE").text}')
        ATPT_OFCDC_SC_CODE = soup.select_one('ATPT_OFCDC_SC_CODE').text
        SD_SCHUL_CODE = soup.select_one('SD_SCHUL_CODE').text
        return ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE
