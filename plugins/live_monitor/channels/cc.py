import re
import ast
import html
import typing as T

import lxml.html

from .base import BaseChannel, LiveCheckResponse


class NetEaseChannel(BaseChannel):
    @property
    def api_url(self) -> str:
        return f'https://cc.163.com/search/all/?query={self.cid}&only=live'

    async def resolve(self, content: str) -> LiveCheckResponse:
        tree: lxml.html.HtmlElement = lxml.html.fromstring(content)
        script: str = ''.join(tree.xpath('body/script[contains(text(),"searchResult")]/text()'))
        script = html.unescape(script)
        script = re.sub(r"u'(.*?)'", lambda match: f"'{match[1]}'", script)
        script = re.search(r"^\s*(?:// )'live': (\[.*\])", script, re.M)[1]
        try:
            lives: T.List[T.Dict[str, T.Any]] = ast.literal_eval(script)
        except:
            lives = []
        for live in lives:
            if str(live['ccid']) == self.cid:
                self.ch_name = live['nickname']
                live_status = 1
                title = live['title']
                cover = live['cover']
                break
        else:
            live_status = 0
            title = ''
            cover = None

        return LiveCheckResponse(name=self.ch_name,
                                 live_status=live_status,
                                 title=title,
                                 url=f'https://cc.163.com/{self.cid}/',
                                 cover=cover)
