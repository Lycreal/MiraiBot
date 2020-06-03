import aiohttp
import lxml.html
import typing as T
from mirai import Mirai, Group, GroupMessage, MessageChain, Image

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


@sub_app.receiver(GroupMessage)
async def find_pic(app: Mirai, group: Group, message: MessageChain):
    if '搜图' in message.toString():
        image: T.Optional[Image] = message.getFirstComponent(Image)
        if image and image.url:
            await app.sendGroupMessage(group, await do_search(image.url))


async def do_search(url: str):
    # saucenao
    s_url = f'https://saucenao.com/search.php?url={url}'

    s_info = await get_saucenao_detail(s_url)

    if s_info and percent_to_int(s_info[0]['Similarity']) > 0.6:
        msg = ''
        for k, v in s_info[0].items():
            if k != 'Content':
                msg += f'{k}: {v}\n'
            else:
                msg += f'{v}\n'
        return msg.strip()
    else:
        msg = '未找到相似图片\n'
        return msg.strip()


async def get_saucenao_detail(s_url):
    async with aiohttp.client.request('GET', s_url) as resp:
        text = await resp.text(encoding='utf8')

    html_e: lxml.html.HtmlElement = lxml.html.fromstring(text)
    results = [
        {
            'Similarity': ''.join(
                r.xpath('.//div[@class="resultsimilarityinfo"]/text()')),
            'Title': ''.join(
                r.xpath('.//div[@class="resulttitle"]/descendant-or-self::text()')),
            'Content': '\n'.join(
                r.xpath('.//div[@class="resultcontentcolumn"]/descendant-or-self::text()')).replace(': \n', ': '),
            'URL': ''.join(
                r.xpath('.//div[@class="resultcontentcolumn"]/a[1]/attribute::href')),
        }
        for r in html_e.xpath('//div[@class="result"]/table[@class="resulttable"]')
    ]
    return results


# 百分数转为int
def percent_to_int(string):
    if string.endswith('%'):
        return float(string.rstrip("%")) / 100
    else:
        return float(string)

# async def shorten_img_url(url: str):
#     i_url = f'https://iqdb.org/?url={url}'
#     async with aiohttp.client.request('GET', i_url) as resp:
#         text = await resp.text(encoding='utf8')
#
#     html_e: lxml.html.HtmlElement = lxml.html.fromstring(text)
#     img_uri = html_e.xpath('//img[contains(attribute::src,"/thu/thu_")]/attribute::src')[0]
#     img_url = f'https://iqdb.org{img_uri}'
#     return img_url
