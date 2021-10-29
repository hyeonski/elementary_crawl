from asyncio import get_event_loop, Semaphore, sleep
from asyncio.events import new_event_loop

from aiohttp import ClientSession
from multidict import CIMultiDictProxy


class Response:
    def __init__(self, status: int, headers: CIMultiDictProxy[str], raw: bytes, encoding: str):
        self.status = status
        self.headers = headers
        self.raw = raw
        self.encoding = encoding

    def text(self) -> str:
        return self.raw.decode(self.encoding)


class Session:
    def __init__(self, num_of_sema: int=5):
        self.session = ClientSession()
        self.semaphore = Semaphore(num_of_sema)
        self.base_url = None

    def __del__(self):
        new_event_loop().run_until_complete(self.session.close())

    async def request(self, method: str, url: str, **kwargs) -> Response:
        if (not url.startswith('http')) and (self.base_url != None):
            url = self.base_url + url
        async with self.semaphore:
            async with self.session.request(method, url, ssl=False, **kwargs) as response:
                raw = await response.read()
                return Response(response.status, response.headers, raw, response.get_encoding())

    async def get(self, url: str, **kwargs) -> Response:
        return await self.request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs) -> Response:
        return await self.request('POST', url, **kwargs)
