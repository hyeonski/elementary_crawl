import os
from typing import List

import pymysql
from dotenv import load_dotenv


class School:
    id: int = None
    name: str = None

    def __init__(self, id: int = None, name: str = None):
        self.id = id
        self.name = name

    def __iter__(self):
        return iter[self.id, self.name]


class PostType:
    id: int = None
    name: str = None

    def __init__(self, id: int = None, name: str = None):
        self.id = id
        self.name = name

    def __iter__(self):
        return iter[self.id, self.name]


class AttachedFile:
    id: int = None
    post_id = None
    data_key: str = None
    name: str = None
    size: int = None
    download_url: str = None

    def __init__(self, id: int = None, post_id: int = None, data_key: str = None, name: str = None, size: int = None, download_url: str = None):
        self.id = id
        self.post_id = post_id
        self.data_key = data_key
        self.name = name
        self.size = size
        self.download_url = download_url

    def __iter__(self):
        return iter([self.id, self.post_id, self.data_key, self.name, self.size, self.download_url])


class Post:
    id: int = None
    school_id: int = None
    post_type_id: int = None
    data_key: str = None
    author: str = None
    upload_at: str = None
    title: str = None
    content: str = None
    attached_files: List[AttachedFile] = None

    def __init__(self,
                 id: int = None, school_id: int = None,
                 post_type_id: int = None, data_key: str = None,
                 author: str = None, upload_at: str = None,
                 title: str = None, content: str = None,
                 attached_files: List[AttachedFile] = None):
        self.id = id
        self.school_id = school_id
        self.post_type_id = post_type_id
        self.data_key = data_key
        self.author = author
        self.upload_at = upload_at
        self.title = title
        self.content = content
        self.attached_files = attached_files

    def __iter__(self):
        return iter([self.id, self.school_id, self.post_type_id, self.data_key, self.author, self.upload_at, self.title, self.content, self.attached_files])


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

    def save_post(self, post: Post) -> int:
        id, school_id, post_type_id, data_key, author, upload_at, title, content, attached_files = post

        with self.db_connection.cursor() as cursor:
            cursor.execute(
                f"SELECT id FROM post WHERE school_id='{school_id}' AND post_type_id='{post_type_id}' AND data_key='{data_key}'")

            id = cursor.fetchone()
            if id is None:
                sql = "INSERT INTO post (school_id, post_type_id, data_key, author, upload_at, title, content) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                cursor.execute(sql, (school_id, post_type_id,
                               data_key, author, upload_at, title, content))
            else:
                id = id[0]
                sql = "UPDATE post SET author=%s, upload_at=%s, title=%s, content=%s WHERE id=%s"
                cursor.execute(
                    sql, (author, upload_at, title, content, id))
            self.db_connection.commit()

            cursor.execute(
                f"SELECT id FROM post WHERE school_id='{school_id}' AND post_type_id='{post_type_id}' AND data_key='{data_key}'")
            id = cursor.fetchone()[0]
            if attached_files is not None:
                self.save_attached_files(id, attached_files)

            print(f'{school_id} {post_type_id} {data_key} 저장됨')
            return id

    def save_attached_files(self, post_id: int, attached_files: List[AttachedFile]):
        with self.db_connection.cursor() as cursor:
            cursor.execute(
                f"DELETE FROM attached_file WHERE post_id='{post_id}'")
            for attached_file in attached_files:
                id, pid, data_key, name, size, download_url = attached_file
                sql = "INSERT INTO attached_file (post_id, data_key, name, size, download_url) VALUES (%s, %s, %s, %s, %s)"
                cursor.execute(
                    sql, (post_id, data_key, name, size, download_url))
            self.db_connection.commit()

    def save_school(self, school_name: str):
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"SELECT id FROM school WHERE name='{school_name}'")
            result = cursor.fetchone()
            if result is None:
                sql = "INSERT INTO school (name) VALUES (%s)"
                cursor.execute(sql, (school_name))
                self.db_connection.commit()
                print(f'{school_name} 저장됨')
            else:
                print(f'{school_name} 이미 저장됨')

    def get_post_type_by_name(self, name: str) -> PostType:
        with self.db_connection.cursor() as cursor:
            cursor.execute(f"SELECT id, name FROM post_type WHERE name='{name}'")
            result = cursor.fetchone()
            return PostType(*result) if result is not None else None

    def get_all_schools(self) -> List[School]:
        with self.db_connection.cursor() as cursor:
            cursor.execute("SELECT id, name FROM school")
            result = cursor.fetchall()
            return [School(*row) for row in result]

    def get_school_by_name(self, school_name: str) -> School:
        with self.db_connection.cursor() as cursor:
            cursor.execute(
                f"SELECT id, name FROM school WHERE name='{school_name}'")
            result = cursor.fetchone()
            return School(*result) if result is not None else None
