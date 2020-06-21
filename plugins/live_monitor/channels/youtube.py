import re
import json
from typing import Dict, Any

import lxml.html

from .base import BaseChannel, LiveCheckResponse


class YoutubeChannel(BaseChannel):
    @property
    def api_url(self):
        return f'https://www.youtube.com/channel/{self.cid}/live'

    async def resolve(self, html_s):
        html: lxml.html.HtmlElement = lxml.html.fromstring(html_s)
        script = ''.join(html.xpath('body/script[contains(text(),"RELATED_PLAYER_ARGS")]/text()'))

        json_s = re.search(r'\'RELATED_PLAYER_ARGS\':(.*),', script)[1]
        RELATED_PLAYER_ARGS = json.loads(json_s)

        json_s = RELATED_PLAYER_ARGS['watch_next_response']
        watch_next_response: Dict[str, Any] = json.loads(json_s)

        videoMetadataRenderer: Dict[str, Any] = \
            watch_next_response['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0][
                'itemSectionRenderer']['contents'][0]['videoMetadataRenderer']

        self.ch_name = ''.join(
            run['text'] for run in videoMetadataRenderer['owner']['videoOwnerRenderer']['title']['runs']
        )

        shareVideoEndpoint = videoMetadataRenderer['shareButton']['buttonRenderer']['navigationEndpoint'][
            'shareVideoEndpoint']

        vid = shareVideoEndpoint['videoId']
        title = shareVideoEndpoint['videoTitle']
        live_url = shareVideoEndpoint['videoShareUrl']

        badges = videoMetadataRenderer.get('badges')
        if badges and 'liveBadge' in badges[0].keys():
            live_status = 1
        else:
            live_status = 0
        return LiveCheckResponse(name=self.ch_name,
                                 live_status=live_status,
                                 title=title,
                                 url=live_url,
                                 cover=f'https://i.ytimg.com/vi/{vid}/hq720.jpg')
