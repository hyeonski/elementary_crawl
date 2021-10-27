import os
from uuid import uuid1

from bs4 import BeautifulSoup
from bs4.element import Tag, Comment
from aiohttp.client_exceptions import InvalidURL

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
                src = elem.get('src')
                extname = os.path.splitext(src)[1]
                try:
                    response = (await session.get(src))
                    if response.status == 200:
                        public_url = upload_image_from_bytes(response.raw, f'{str(uuid1())}{extname}')
                        elem['src'] = public_url
                    else: raise Exception(f'{response.status}')
                except Exception:
                    elem['src'] = ''
            else:
                await manip_board_content(session, elem)
        if isinstance(elem, Comment):
            elem.extract()
