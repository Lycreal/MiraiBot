import re
import json

import lxml.html

from .base import BaseChannel, LiveCheckResponse


class NetEaseChannel(BaseChannel):
    @property
    def api_url(self):
        return f'https://cc.163.com/{self.cid}/'

    async def resolve(self, html_s):
        html_element: lxml.html.HtmlElement = lxml.html.fromstring(html_s)
        try:
            script = html_element.xpath('//script[@id="__NEXT_DATA__"]/text()')[0]
            room_info = json.loads(script)['props']['pageProps']['roomInfoInitData']

            title = room_info['live']['title']
            hot_score = room_info['live']['hot_score']
            live_status = 1 if hot_score > 0 else 0

            ch_name = room_info['micfirst']['nickname']
            self.ch_name = ch_name

        except IndexError:
            # 旧格式，计划弃用
            script = html_element.xpath('//script[contains(text(),"var roomInfo")]/text()')[0]
            live = re.search(r'isLive', script)
            if live:
                live_status = re.search(r'[\'\"]?isLive[\'\"]? ?: ?[\'\"]?(\d)[\'\"]?', script).group(1)
                self.ch_name = re.search(r'[\'\"]?anchorName[\'\"]? ?: ?[\'\"]?([^\'\"]+)[\'\"]?', script).group(1)
                title = re.search(r'[\'\"]?title[\'\"]? ?: ?[\'\"]?([^\'\"]+)[\'\"]?', script).group(1)
                title = title.replace('\\u0026', '&')
            else:
                live_status = 0
                title = ''

        return LiveCheckResponse(name=self.ch_name,
                                 live_status=live_status,
                                 title=title,
                                 url=f'https://cc.163.com/{self.cid}/',
                                 cover=None)
