from asyncio import get_event_loop, Semaphore

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
    def __init__(self):
        self.session = ClientSession()
        self.semaphore = Semaphore(5)

    def __del__(self):
        get_event_loop().run_until_complete(self.session.close())

    async def request(self, method: str, url: str, **kwargs):
        async with self.semaphore:
            async with self.session.request(method, url, ssl=False, **kwargs) as response:
                raw = await response.read()
                return Response(response.status, response.headers, raw, response.get_encoding())

    async def get(self, url: str, **kwargs):
        return await self.request('GET', url, **kwargs)

    async def post(self, url: str, **kwargs):
        return await self.request('POST', url, **kwargs)
