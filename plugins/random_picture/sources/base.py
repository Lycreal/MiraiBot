import abc
import aiohttp
import typing as T

from pydantic import BaseModel


class PictureSource(BaseModel, abc.ABC):
    api_url: str
    encoding: str = 'utf8'
    keywords: T.List[str] = []

    async def get(self, *args, **kwargs):
        content = await self.fetch()
        image_url = self.resolve(content)
        return image_url

    async def fetch(self):
        async with aiohttp.request('GET', self.api_url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            return await resp.text(self.encoding)

    @abc.abstractmethod
    async def resolve(self, content: str):
        return NotImplementedError
