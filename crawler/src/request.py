from time import sleep

from requests import Session
from requests.models import Response

from util import print_log

class MySession:
    def __init__(self):
        self.session = Session()
        self.base_url = None

    def request(self, method: str, url: str, **kwargs) -> Response:
        retry_cnt = 0
        max_retry = 5

        if (not url.startswith('http')) and (self.base_url != None):
            url = self.base_url + url
        while True:
            response = self.session.request(method, url, **kwargs)
            if response.status_code != 502:
                return response
            if retry_cnt < max_retry:
                print_log('502 error, retry')
                retry_cnt += 1
				sleep(5)
            else: 
                print_log('502 error, retry failed')
                return response


    def get(self, url: str, **kwargs) -> Response:
        return self.request('GET', url, **kwargs)

    def post(self, url: str, **kwargs) -> Response:
        return self.request('POST', url, **kwargs)
