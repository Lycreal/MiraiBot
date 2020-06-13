import json

import aiohttp

from .base import BaseChannel, LiveCheckResponse


class BiliChannel(BaseChannel):
    @property
    def api_url(self):
        return f'https://api.live.bilibili.com/room/v1/Room/get_info?id={self.cid}'

    async def resolve(self, html_s):
        json_d: dict = json.loads(html_s)

        if not self.ch_name:
            uid: int = json_d['data']['uid']
            self.ch_name = await self.get_name(uid)

        return LiveCheckResponse(name=self.ch_name,
                                 live_status=json_d['data']['live_status'],
                                 title=json_d['data']['title'],
                                 url=f'https://live.bilibili.com/{self.cid}',
                                 cover=json_d['data']['user_cover'])

    @staticmethod
    async def get_name(uid: int) -> str:
        url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
        async with aiohttp.request('GET', url, timeout=aiohttp.ClientTimeout(10)) as resp:
            j = await resp.json(encoding='utf-8')
        name = j['data']['name']
        return name
