import asyncio
import os

import requests
from dotenv import load_dotenv
from bs4 import BeautifulSoup

from database import DBManager
from crawler.seoul_seoi import SeoulSeoiCrawler
from school_meal import SchoolMealCrawler


def save_all_schools():
    db_manager = DBManager()
    pSize = 1000
    pIndex = 1
    while True:
        response = requests.get('https://open.neis.go.kr/hub/schoolInfo', params={
            'key': os.environ['NEIS_OPEN_API_KEY'],
            'Type': 'xml',
            'SCHUL_KND_SC_NM': '초등학교',
            'pSize': pSize,
            'pIndex': pIndex,
        })
        soup = BeautifulSoup(response.text, 'xml')
        code = soup.select_one('RESULT > CODE').text
        if code == 'INFO-200':
            break
        elif code != 'INFO-000':
            raise Exception(f'초등학교 목록 크롤링 중 알 수 없는 오류 발생: {code}')
        for item in soup.select('row'):
            school_name = item.select_one('SCHUL_NM').text
            db_manager.save_school_data(school_name)

        pIndex += 1


def exception_handler(loop, context):
    print(context)
    exit(1)


def main():
    load_dotenv(verbose=True)
    save_all_schools()
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exception_handler)
    # crawler = SeoulSeoiCrawler('https://seo2.sen.es.kr/')
    # loop.run_until_complete(crawler.run())
    # crawler = SchoolMealCrawler()
    # loop.run_until_complete(crawler.run())


if __name__ == "__main__":
    main()
