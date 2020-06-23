import re
import json
from typing import Dict, Any

import lxml.html

from .base import BaseChannel, LiveCheckResponse


class YoutubeChannel(BaseChannel):
    @property
    def api_url(self):
        return f'https://www.youtube.com/channel/{self.cid}/live'

    async def resolve(self, content: str):
        tree: lxml.html.HtmlElement = lxml.html.fromstring(content)

        if script := ''.join(tree.xpath('body/script[contains(text(),"RELATED_PLAYER_ARGS")]/text()')):
            script = re.search(r'\'RELATED_PLAYER_ARGS\':(.*),', script)[1]
            watch_next_response: Dict[str, Any] = json.loads(json.loads(script)['watch_next_response'])

            videoMetadataRenderer: Dict[str, Any] = watch_next_response['contents']['twoColumnWatchNextResults']['results']['results']['contents'][0]['itemSectionRenderer']['contents'][0]['videoMetadataRenderer']
            shareVideoEndpoint: Dict[str, Any] = videoMetadataRenderer['shareButton']['buttonRenderer']['navigationEndpoint']['shareVideoEndpoint']

            self.ch_name = ''.join(run['text'] for run in videoMetadataRenderer['owner']['videoOwnerRenderer']['title']['runs'])
            badges = videoMetadataRenderer.get('badges')
            live_status = 1 if badges and 'liveBadge' in badges[0].keys() else 0
            vid = shareVideoEndpoint['videoId']
            title = shareVideoEndpoint['videoTitle']
            live_url = shareVideoEndpoint['videoShareUrl']

        elif script := ''.join(tree.xpath('//div[@id="player-wrap"]/script[contains(text(),"player_response")]/text()')):
            script = re.search(r'ytplayer.config = ({.*?});', script)[1]
            script = json.loads(script)['args']['player_response']
            videoDetails: Dict[str, Any] = json.loads(script)['videoDetails']

            self.ch_name = videoDetails['author']
            live_status = videoDetails.get('isLive', 0)
            title = videoDetails['title']
            vid = videoDetails['videoId']
            live_url = f'https://youtu.be/{vid}'
        else:
            raise AssertionError

        return LiveCheckResponse(name=self.ch_name,
                                 live_status=live_status,
                                 title=title,
                                 url=live_url,
                                 cover=f'https://i.ytimg.com/vi/{vid}/hq720.jpg')
