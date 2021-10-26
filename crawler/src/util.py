from bs4 import BeautifulSoup


def get_form_data_from_inputs(response_text: str, form_data: dict):
    soup = BeautifulSoup(response_text, 'html.parser')

    inputs = soup.select('input[type=hidden]')
    for input in inputs:
        value = input.get('value')
        form_data[input.get('name')] = value if value != None else ''
