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
        if '"isLive":true' not in content and self.cid in content:
            return LiveCheckResponse(
                name=self.ch_name,
                live_status=0,
                title='',
                url=self.api_url,
                cover=None
            )

        if resp := self.parse_html_1(content):
            return resp
        elif resp := self.parse_html_2(content):
            return resp
        elif resp := self.parse_html_3(content):
            return resp
        elif resp := self.parse_html_4(content):
            return resp
        else:
            # ========== DEBUG ==========
            import os
            from config import data_path
            debug_filepath = os.path.join(data_path, 'youtube_live_debug.html')
            with open(debug_filepath, 'w', encoding='utf8') as f:
                f.write(content)
            # ========== DEBUG ==========

            raise AssertionError(f'获取直播间信息失败, html页面保存至{debug_filepath}')

    def parse_html_1(self, content: str):
        if 'videoDetails' in content:
            try:
                tree: lxml.html.HtmlElement = lxml.html.fromstring(content)
                script = ''.join(tree.xpath('body/script[contains(text(),"ytInitialPlayerResponse")]/text()'))
                script = re.search(r'var ytInitialPlayerResponse = ({.*});', script)[1]
                videoDetails = json.loads(script)['videoDetails']
                return self.parse_videoDetails(videoDetails)
            except:
                return None

    def parse_html_2(self, content: str):
        if 'videoDetails' in content:
            try:
                tree: lxml.html.HtmlElement = lxml.html.fromstring(content)
                script = ''.join(tree.xpath('body/script[contains(text(),"ytInitialPlayerResponse")]/text()'))
                script = re.search(r'window\["ytInitialPlayerResponse"] = ({.*?});', script)[1]
                videoDetails = json.loads(script)['videoDetails']
                return self.parse_videoDetails(videoDetails)
            except:
                return None

    def parse_html_3(self, content: str):
        if 'videoDetails' in content:
            try:
                tree: lxml.html.HtmlElement = lxml.html.fromstring(content)
                script = ''.join(tree.xpath('//div[@id="player-wrap"]/script[contains(text(),"player_response")]/text()'))
                script = re.search(r'ytplayer.config = ({.*?});', script)[1]
                script = json.loads(script)['args']['player_response']
                videoDetails: Dict[str, Any] = json.loads(script)['videoDetails']
                return self.parse_videoDetails(videoDetails)
            except:
                return None

    def parse_html_4(self, content: str):
        try:
            tree: lxml.html.HtmlElement = lxml.html.fromstring(content)
            script = ''.join(tree.xpath('body/script[contains(text(),"RELATED_PLAYER_ARGS")]/text()'))
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
            return LiveCheckResponse(
                name=self.ch_name,
                live_status=live_status,
                title=title,
                url=live_url,
                cover=f'https://i.ytimg.com/vi/{vid}/hq720.jpg'
            )
        except:
            return None

    def parse_videoDetails(self, videoDetails: dict):
        self.ch_name = videoDetails['author']
        live_status = videoDetails.get('isLive', 0)
        title = videoDetails['title']
        vid = videoDetails['videoId']
        live_url = f'https://youtu.be/{vid}'
        return LiveCheckResponse(
            name=self.ch_name,
            live_status=live_status,
            title=title,
            url=live_url,
            cover=f'https://i.ytimg.com/vi/{vid}/hq720.jpg'
        )
