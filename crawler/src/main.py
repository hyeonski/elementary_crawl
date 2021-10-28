import asyncio

from dotenv import load_dotenv

from crawler.seoul_seoi import SeoulSeoiCrawler
from school_meal import SchoolMealCrawler

def exception_handler(loop, context):
    print(context)
    exit(1)


def main():
    load_dotenv(verbose=True)
    loop = asyncio.get_event_loop()
    loop.set_exception_handler(exception_handler)
    # crawler = SeoulSeoiCrawler('https://seo2.sen.es.kr/')
    # loop.run_until_complete(crawler.run())
    crawler = SchoolMealCrawler()
    loop.run_until_complete(crawler.run())


if __name__ == "__main__":
    main()
