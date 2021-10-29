import asyncio
from typing import List

from dotenv import load_dotenv
from crawler.crawler import ACrawler

from crawler.school.seoul_seoi import SeoulSeoiCrawler
from crawler.school.jeonju_inbong import JeonjuInbongCrawler
from crawler.school_meal import SchoolMealCrawler


def exception_handler(loop, context):
    print(context)
    exit(1)


async def run_crawlers():
    crawlers: List[ACrawler] = [
        SeoulSeoiCrawler('서울서이초등학교', 'https://seo2.sen.es.kr'),
        JeonjuInbongCrawler('전주인봉초등학교', 'https://school.jbedu.kr/inbong'),
    ]
    coros = [crawler.run() for crawler in crawlers]
    await asyncio.gather(*coros)


def main():
    load_dotenv(verbose=True)
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exception_handler)
    loop.run_until_complete(run_crawlers())


if __name__ == "__main__":
    main()
