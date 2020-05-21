import json
import typing as T
import aiohttp

# {uid:dynamic_id}
LAST: T.Dict[int, int] = {}


async def GetDynamicStatus(uid: int, debug=0):
    cards_data = await getCards(uid)

    last_dynamic = LAST.setdefault(uid, cards_data[0]['desc']['dynamic_id'])

    for i, card_data in enumerate(cards_data):
        if last_dynamic == card_data['desc']['dynamic_id']:
            break
    else:  # 没有找到上次动态，可能为程序初次运行或动态被删除
        LAST[uid] = cards_data[0]['desc']['dynamic_id']
        return '', []

    if debug:
        i = debug

    if i >= 1:
        LAST[uid] = cards_data[i - 1]['desc']['dynamic_id']
        return CardData(card_data).resolve()
    else:
        return '', []  # 没有新动态


async def getCards(uid: int) -> T.List[dict]:
    url = 'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history'
    params = {
        'host_uid': str(uid),
        'offset_dynamic_id': '0'
    }
    async with aiohttp.request('GET', url, params=params) as resp:
        res = await resp.read()
    cards_data = json.loads(res)
    return cards_data['data']['cards']


class CardData(dict):
    def __init__(self, obj):
        obj['card'] = deep_decode(obj['card'])
        super(CardData, self).__init__(obj)

    def resolve(self) -> T.Tuple[str, T.List[str]]:
        name = self["desc"]["user_profile"]["info"]["uname"]
        type = self['desc']['type']
        origin_name = self['card']['origin_user']['info']['uname'] if type == 1 else None
        origin_type = self['desc']['origin']['type'] if type == 1 else None

        msg, imgs = Card(self['card'], type).resolve(name, type, origin_name, origin_type)
        msg += f"\n\n本条动态的地址为: https://t.bilibili.com/{self['desc']['dynamic_id']}"
        return msg, imgs


def deep_decode(j: T.Union[dict, str]):
    if isinstance(j, dict):
        for k, v in j.items():
            j[k] = deep_decode(v)
    elif isinstance(j, str):
        try:
            j = deep_decode(json.loads(j))
        except json.decoder.JSONDecodeError:
            pass
    return j


class Card(dict):
    def __init__(self, obj, c_type):
        super(Card, self).__init__(obj)
        if c_type in [1, 4]:
            self.content = self['item'].get('content')
        elif c_type == 2:
            self.description = self['item'].get('description')
        elif c_type == 8:
            self.dynamic = self.get('dynamic')
            self.title = self.get('title')
            self.pic = self.get('pic')
        elif c_type == 64:
            self.dynamic = self.get('dynamic')
            self.title = self.get('title')
            self.banner_url = self.get('banner_url')
        elif c_type == 4200:
            self.roomid = self.get('roomid')
            self.cover = self.get('user_cover') or self.get(['cover'])
            self.title = self.get('title')

    def resolve(self, name: str, c_type: int, origin_name: str = 0, origin_type: int = 0) -> T.Tuple[str, T.List[str]]:
        img_urls = []
        if c_type == 1:  # 转发
            msg = f'{name}的转发：{self.content}\n原动态：'
            msg_a, img_urls_a = Card(self['origin'], origin_type).resolve(origin_name, origin_type)
            msg += msg_a
            img_urls += img_urls_a
        elif c_type == 2:  # 图片动态
            msg = f'{name}的新动态：{self.description}'
            img_urls += [pic_info['img_src'] for pic_info in self['item']['pictures']]
        elif c_type == 4:  # 文字动态
            msg = f'{name}的新动态：{self.content}'
        elif c_type == 8:  # 视频动态
            msg = f'{name}的新视频「{self.title}」：{self.dynamic}'
            img_urls += [self.pic]
        elif c_type == 64:  # 专栏动态
            msg = f'{name}的新专栏「{self.title}」：{self.dynamic}'
            img_urls += [self.banner_url]
        elif c_type == 2048:  # 头像框动态
            msg = '头像框动态'
        elif c_type == 4200:  # 直播间动态
            msg = f'{name}的直播间：{self.title} https://live.bilibili.com/{self.roomid}'
            img_urls += [self.cover]
        else:  # 未知
            msg = '未知动态类型'
        return msg, img_urls
