from typing import List

from dotenv import load_dotenv
from crawler.crawler import ACrawler

from crawler.school.seoul_seoi import SeoulSeoiCrawler
from crawler.school.jeonju_inbong import JeonjuInbongCrawler
from crawler.school_meal import SchoolMealCrawler


def main():
    load_dotenv(verbose=True)
    crawlers: List[ACrawler] = [
        SchoolMealCrawler(),
        SeoulSeoiCrawler('서울서이초등학교', 'https://seo2.sen.es.kr'),
        JeonjuInbongCrawler('전주인봉초등학교', 'https://school.jbedu.kr/inbong'),
    ]
    for crawler in crawlers:
        crawler.run()


if __name__ == "__main__":
    main()
