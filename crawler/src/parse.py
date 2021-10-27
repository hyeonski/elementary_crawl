import os
from uuid import uuid1

from bs4 import BeautifulSoup
from bs4.element import Tag, Comment

from request import Session
from upload_file import upload_image_from_bytes


def get_form_data_from_inputs(response_text: str, form_data: dict):
    soup = BeautifulSoup(response_text, 'html.parser')
    inputs = soup.select('input[type=hidden]')
    for input in inputs:
        value = input.get('value')
        form_data[input.get('name')] = value if value != None else ''


async def manip_board_content(session: Session, tag: Tag):
    for elem in tag.contents:
        if isinstance(elem, Tag):
            if elem.name == 'img':
                await upload_image_and_replace_src(session, elem)
            else:
                await manip_board_content(session, elem)
        if isinstance(elem, Comment):
            elem.extract()


async def upload_image_and_replace_src(session: Session, img_tag: Tag):
    src = img_tag.get('src')
    extname = os.path.splitext(src)[1]
    try:
        response = (await session.get(src))
        if response.status == 200:
            public_url = upload_image_from_bytes(response.raw, f'{str(uuid1())}{extname}')
            img_tag['src'] = public_url
        else:
            raise Exception(f'{response.status}')
    except Exception:
        img_tag['src'] = ''
