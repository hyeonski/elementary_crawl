from pymysql import Connection
from pymysql.cursors import Cursor

from utils import print_error_endl


class Post:
    def __init__(self, post_type_id, data_key, author, upload_at, title, content):
        self.post_type_id = post_type_id
        self.data_key = data_key
        self.author = author
        self.upload_at = upload_at
        self.title = title
        self.content = content

    def __iter__(self):
        return iter([self.post_type_id, self.data_key, self.author, self.upload_at, self.title, self.content])


class AttachedFile:
    def __init__(self, post_data_key, attached_file_id, file_sn, name, size):
        self.post_data_key = post_data_key
        self.attached_file_id = attached_file_id
        self.file_sn = file_sn
        self.name = name
        self.size = size
        self.preview_url = f'http://viewhosting.ssem.or.kr:8080/SynapDocViewServer/job?fid={attached_file_id}_{file_sn}&filePath=https://seo2.sen.es.kr:443/dggb/cnvrFileDown.do?atchFileId={attached_file_id}:{file_sn}&convertType=0&fileType=URL&sync=true'
        self.download_url = f'https://seo2.sen.es.kr/dggb/board/boardFile/downFile.do?atchFileId={attached_file_id}&fileSn={str(file_sn)}'

    def __iter__(self):
        return iter([self.post_data_key, self.attached_file_id, self.file_sn, self.name, self.size, self.preview_url, self.download_url])


def store_post_data(db_connection: Connection, post_data: Post):
    post_type_id, data_key, author, upload_at, title, content = post_data
    title = db_connection.escape_string(title)
    content = db_connection.escape_string(content)

    cursor: Cursor = db_connection.cursor()
    cursor.execute(f"SELECT data_key FROM post WHERE data_key='{data_key}'")
    if cursor.fetchone() == None:
        cursor.execute(
            f"INSERT INTO post (data_key, post_type_id, author, upload_at, title, content) VALUES ('{data_key}', '{post_type_id}', '{author}', '{upload_at}', '{title}', '{content}')")
    else:
        cursor.execute(
            f"UPDATE post SET author='{author}', upload_at='{upload_at}', title='{title}', content='{content}' WHERE data_key='{data_key}'")
    db_connection.commit()


def store_file_data(db_connection: Connection, file: AttachedFile):
    post_data_key, attached_file_id, file_sn, name, size, preview_url, download_url = file
    name = db_connection.escape_string(name)
    preview_url = db_connection.escape_string(preview_url)
    download_url = db_connection.escape_string(download_url)

    cursor: Cursor = db_connection.cursor()
    cursor.execute(f"SELECT id FROM post WHERE data_key='{post_data_key}'")
    ids = cursor.fetchone()
    if ids == None:
        print_error_endl(f'Post data key {post_data_key} not found')
        exit()
    post_id = ids[0]

    cursor.execute(
        f"INSERT INTO attached_file (post_id, attached_file_id, file_sn, name, size, preview_url, download_url) VALUES ('{post_id}', '{attached_file_id}', '{file_sn}', '{name}', '{size}', '{preview_url}', '{download_url}')")
    db_connection.commit()
