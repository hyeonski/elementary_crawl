from abc import ABCMeta, abstractmethod
import asyncio

from database import DBManager
from request import Session


class ACrawler(metaclass=ABCMeta):
    def __init__(self, school_main_url: str):
        asyncio.get_event_loop().run_until_complete(self.start_session(school_main_url))
        self.db_manager = DBManager()

    async def start_session(self, school_main_url: str):
        self.session = Session()
        await self.session.get(school_main_url, allow_redirects=False)

    def __del__(self):
        del self.session
        del self.db_manager

    async def run(self):
        tasks = [
            self.crawl_notice(),
            self.crawl_parent_letter(),
            self.crawl_school_meal_news(),
        ]
        await asyncio.gather(*tasks)

    @abstractmethod
    async def crawl_notice(self):
        pass

    @abstractmethod
    async def crawl_parent_letter(self):
        pass

    @abstractmethod
    async def crawl_school_meal_news(self):
        pass
