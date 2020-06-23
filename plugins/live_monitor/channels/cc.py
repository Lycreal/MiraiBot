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
        script = re.search(r"'anchor': (\[.*\]|)", html.unescape(script), re.M)[1]
        anchors: T.List[T.Dict[str, T.Any]] = ast.literal_eval(script) if script else []

        for anchor in anchors:
            if str(anchor['cuteid']) == self.cid:
                self.ch_name = anchor['nickname']
                live_status = anchor['status']
                title = anchor['title']
                cover = anchor['cover']
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
