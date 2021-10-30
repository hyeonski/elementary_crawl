from typing import List
from threading import Thread

from dotenv import load_dotenv
from crawler.crawler import ACrawler

from crawler.school.seoul_seoi import SeoulSeoiCrawler
from crawler.school.jeonju_inbong import JeonjuInbongCrawler
from crawler.school_meal import SchoolMealCrawler

def worker(crawler: ACrawler):
    crawler.run()


def main():
    load_dotenv(verbose=True)
    crawlers: List[ACrawler] = [
        SchoolMealCrawler(),
        SeoulSeoiCrawler('서울서이초등학교', 'https://seo2.sen.es.kr'),
        JeonjuInbongCrawler('전주인봉초등학교', 'https://school.jbedu.kr/inbong'),
    ]
    threads = [Thread(target=worker, args=(crawler,)) for crawler in crawlers]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()
