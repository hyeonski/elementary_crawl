import os

import pymysql
from dotenv import load_dotenv


class AttachedFile:
    def __init__(self, data_key, name, size, download_url):
        self.data_key = data_key
        self.name = name
        self.size = size
        self.download_url = download_url

    def __iter__(self):
        return iter([self.data_key, self.name, self.size, self.download_url])


class Post:
    def __init__(self, school_name, post_type_name, data_key, author, upload_at, title, content, attached_files=None):
        self.school_name = school_name
        self.post_type_name = post_type_name
        self.data_key = data_key
        self.author = author
        self.upload_at = upload_at
        self.title = title
        self.content = content
        self.attached_files = attached_files

    def __iter__(self):
        return iter([self.school_name, self.post_type_name, self.data_key, self.author, self.upload_at, self.title, self.content, self.attached_files])


class DBManager:
    def __init__(self):
        load_dotenv(verbose=True)
        host = os.environ['DB_HOST']
        user = os.environ['DB_USER']
        password = os.environ['DB_PASSWORD']
        database = os.environ['DB_DATABASE']
        self.db_connection = pymysql.connect(
            host=host, user=user, password=password, db=database, charset='utf8')

    def __del__(self):
        self.db_connection.close()

    def store_post_data(self, post: Post):
        school_name, post_type_name, data_key, author, upload_at, title, content, attached_files = post
        title = self.db_connection.escape_string(title)
        content = self.db_connection.escape_string(content)

        with self.db_connection.cursor() as cursor:
            cursor.execute(f"SELECT id FROM school WHERE name='{school_name}'")
            school_id = cursor.fetchone()[0]
            cursor.execute(f"SELECT id FROM post_type WHERE name='{post_type_name}'")
            post_type_id = cursor.fetchone()[0]
            cursor.execute(f"SELECT id FROM post WHERE school_id='{school_id}' AND post_type_id='{post_type_id}' AND data_key='{data_key}'")

            post_id = cursor.fetchone()
            if post_id is None:
                sql = "INSERT INTO post (school_id, post_type_id, data_key, author, upload_at, title, content) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (school_id, post_type_id, data_key, author, upload_at, title, content))
            else:
                post_id = post_id[0]
                sql = "UPDATE post SET author=%s, upload_at=%s, title=%s, content=%s WHERE id=%s"
                cursor.execute(
                    sql, (author, upload_at, title, content, post_id))
            self.db_connection.commit()
            print(f'{school_name} {post_type_name} {data_key} 저장됨')

            if attached_files is not None:
                cursor.execute(f"SELECT id FROM post WHERE school_id='{school_id}' AND post_type_id='{post_type_id}' AND data_key='{data_key}'")
                post_id = cursor.fetchone()
                if post_id is None:
                    # 에러처리 필요
                    return
                else:
                    post_id = post_id[0]
                    cursor.execute(f"DELETE FROM attached_file WHERE post_id='{post_id}'")
                    for attached_file in attached_files:
                        data_key, name, size, download_url = attached_file
                        name = self.db_connection.escape_string(name)
                        download_url = self.db_connection.escape_string(download_url)
                        sql = "INSERT INTO attached_file (post_id, data_key, name, size, download_url) VALUES (%s, %s, %s, %s, %s)"
                        cursor.execute(sql, (post_id, data_key, name, size, download_url))
                        print(f'{school_name} {post_type_name} 첨부파일 {data_key} 저장됨')
                    self.db_connection.commit()
