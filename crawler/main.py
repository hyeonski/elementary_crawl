from multiprocessing import Pool, Process
from locale import setlocale, LC_TIME
import pymysql
from crawl_board import crawl_board
from crawl_menu import crawl_school_meal_menu


def board_worker(board_url, post_type_name):
    db_connection = pymysql.connect(host='localhost', user='root', password='1234', db='elementary', charset='utf8')

    # post type id 가져오기
    cursor = db_connection.cursor()
    cursor.execute(f"SELECT id FROM post_type WHERE name='{post_type_name}'")
    post_type_id = cursor.fetchone()[0]

    crawl_board(board_url, post_type_id, db_connection)
    db_connection.close()


def school_meal_worker(board_url):
    db_connection = pymysql.connect(host='localhost', user='root', password='1234', db='elementary', charset='utf8')

    cursor = db_connection.cursor()
    cursor.execute(f"SELECT id FROM post_type WHERE name='school_meal_menu'")
    post_type_id = cursor.fetchone()[0]

    setlocale(LC_TIME, 'ko_KR.UTF-8') # 한글 날짜 파싱을 위한 설정
    crawl_school_meal_menu(board_url, post_type_id, db_connection)
    db_connection.close()


if __name__ == '__main__':
    process = Process(target=school_meal_worker, args=('https://seo2.sen.es.kr/78586/subMenu.do',))
    process.start()

    boards = [
        ('https://seo2.sen.es.kr/78584/subMenu.do', 'notice'),
        ('https://seo2.sen.es.kr/78585/subMenu.do', 'parent_letter'),
        ('https://seo2.sen.es.kr/113876/subMenu.do', 'school_meal'),
    ]

    with Pool(processes=len(boards)) as pool:
        pool.starmap(board_worker, boards)

    process.join()
