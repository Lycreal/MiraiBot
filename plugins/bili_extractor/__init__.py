import typing as T
from mirai import Mirai, Group, GroupMessage, MessageChain, LightApp, Plain, Image
import re
import json
import asyncio
import aiohttp
import lxml.html
import urllib.parse

__plugin_name__ = 'B站小程序解析'
__plugin_usage__ = r'''自动解析B站小程序分享链接，显示视频标题并推测视频链接'''

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


@sub_app.receiver(GroupMessage)
async def extract(app: Mirai, group: Group, message: MessageChain):
    light_app: T.Optional[LightApp] = message.getFirstComponent(LightApp)
    if light_app:
        content: dict = json.loads(light_app.content)
        if content.get("prompt") == "[QQ小程序]哔哩哔哩":
            title: str = content['meta']['detail_1']['desc']
            url = content['meta']['detail_1'].get('qqdocurl')
            if not url:
                url = await search_bili_by_title(title)
            url = shorten(url) if url else '未找到视频地址'
            preview = content['meta']['detail_1'].get('preview')
            if not urllib.parse.urlparse(preview).scheme:
                preview = 'http://' + preview
            await app.sendGroupMessage(group, [Plain(f'{title}\n{url}\n'), await Image.fromRemote(preview)])


def shorten(_url: str) -> str:
    url_patterns = (
        re.compile(r'/(av\d+|BV\w+)'),
        re.compile(r'/(ep\d+)'),
        re.compile(r'b23.tv/(\w+)'),
    )
    for p in url_patterns:
        vid = p.search(_url)
        if vid:
            _url = f'https://b23.tv/{vid[1]}'
            break
    return _url


async def search_bili_by_title(title: str) -> T.Optional[str]:
    """
    :return: url
    """
    # remove brackets
    brackets_pattern = re.compile(r'[()\[\]{}（）【】]')
    title_without_brackets = brackets_pattern.sub(' ', title).strip()
    search_url = f'https://search.bilibili.com/video?keyword={urllib.parse.quote(title_without_brackets)}'

    try:
        async with aiohttp.request('GET', search_url, timeout=aiohttp.client.ClientTimeout(10)) as resp:
            text = await resp.text(encoding='utf8')
            content: lxml.html.HtmlElement = lxml.html.fromstring(text)
    except asyncio.TimeoutError:
        return None

    for video in content.xpath('//li[@class="video-item matrix"]/a[@class="img-anchor"]'):
        if title == ''.join(video.xpath('./attribute::title')):
            url = ''.join(video.xpath('./attribute::href'))
            break
    else:
        url = None
    return url
