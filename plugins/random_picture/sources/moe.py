import aiohttp
import typing as T

from .base import PictureSource


class MoePicture(PictureSource):
    # https://api.blogbig.cn/random/
    api_url: str = 'https://api.blogbig.cn/random/api.php'
    keywords: T.List[str] = ['二次元']

    async def fetch(self):
        async with aiohttp.request('GET', self.api_url, allow_redirects=False) as resp:
            return resp.headers['Location']

    def resolve(self, content: str):
        return content
