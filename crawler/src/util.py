from typing import List

from bs4 import BeautifulSoup
from bs4.element import PageElement


def parse_base_url(url: str) -> str:
    urlscheme, path = url.split('://')
    if len(path.split('/')) == 1:
        return url
    else:
        return urlscheme + '://' + path.split('/')[0]

def stringify_tags(tags: List[PageElement]) -> str:
    return ''.join([str(tag) for tag in tags])

def get_form_data_from_inputs(response_text: str, form_data: dict):
        soup = BeautifulSoup(response_text, 'html.parser')
        inputs = soup.select('input[type=hidden]')
        for input in inputs:
            value = input.get('value')
            form_data[input.get('name')] = value if value != None else ''
