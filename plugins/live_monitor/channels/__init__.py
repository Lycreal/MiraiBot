"""
example
channel = BiliChannel('2')
while asyncio.sleep(5):
    resp = await channel.update()
    if resp:
        print(resp.title)
"""

from .base import BaseChannel, LiveCheckResponse
from .bili import BiliChannel
from .youtube import YoutubeChannel
from .cc import NetEaseChannel

__all__ = ['BaseChannel', 'LiveCheckResponse',
           'BiliChannel', 'YoutubeChannel', 'NetEaseChannel']
