import asyncio

from dotenv import load_dotenv

from crawler.seoul_seoi import SeoulSeoiCrawler


def main():
    load_dotenv(verbose=True)
    loop = asyncio.get_event_loop()
    crawler = SeoulSeoiCrawler()
    loop.run_until_complete(crawler.run())


if __name__ == "__main__":
    main()
