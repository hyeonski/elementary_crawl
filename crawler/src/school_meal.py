from asyncio.tasks import Task
from typing import List, Tuple
import os
from asyncio import gather, create_task
from datetime import datetime

from bs4 import BeautifulSoup

from request import Session
from database import DBManager, Post


class SchoolMealCrawler():
    def __init__(self):
        self.key = os.environ['NEIS_OPEN_API_KEY']
        self.session = Session()
        self.db_manager = DBManager()

    def __del__(self):
        del self.session
        del self.db_manager

    async def run(self):
        coro: List[Task] = []
        school_name_list = self.db_manager.get_all_school_names()
        for school_name in school_name_list:
            coro.append(create_task(self.get_school_meal(school_name)))
        await gather(*coro)

    async def get_school_meal(self, school_name: str):
        now = datetime.now()
        ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE = await self.get_school_code(school_name)
        pSize = 1000
        pIndex = 1
        response = await self.session.get('https://open.neis.go.kr/hub/mealServiceDietInfo', params={
            'key': self.key,
            'Type': 'xml',
            'ATPT_OFCDC_SC_CODE': ATPT_OFCDC_SC_CODE,
            'SD_SCHUL_CODE': SD_SCHUL_CODE,
            'pSize': pSize,
            'pIndex': pIndex,
            'MLSV_FROM_YMD': datetime(now.year, now.month, 1).strftime('%Y%m%d'),
        })
        soup = BeautifulSoup(response.text(), 'xml')
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
            self.db_manager.store_post_data(Post(
                school_name=school_name,
                post_type_name='오늘의 급식',
                data_key=date.strftime('%Y%m%d'),
                author=school_name,
                upload_at=date.strftime('%Y-%m-%d'),
                title=f'{date.strftime("%Y년 %m월 %d일")} [{meal_type}]',
                content=f'<p>{menu}</p>',
            ))

    async def get_school_code(self, school_name: str) -> Tuple[str, str]:
        response = await self.session.get('https://open.neis.go.kr/hub/schoolInfo', params={
            'key': self.key,
            'Type': 'xml',
            'SCHUL_NM': school_name
        })
        soup = BeautifulSoup(response.text(), 'xml')
        if soup.select_one('RESULT > CODE').text != 'INFO-000':
            raise Exception(f'해당하는 학교 정보가 없습니다.: {soup.select_one("RESULT > CODE").text}')
        ATPT_OFCDC_SC_CODE = soup.select_one('ATPT_OFCDC_SC_CODE').text
        SD_SCHUL_CODE = soup.select_one('SD_SCHUL_CODE').text
        return ATPT_OFCDC_SC_CODE, SD_SCHUL_CODE
