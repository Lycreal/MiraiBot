import json
import typing as T
import aiohttp
from collections import namedtuple

# {uid:dynamic_id}
LAST: T.Dict[int, int] = {}

Resp = namedtuple('Resp', 'msg imgs dynamic_id')


async def GetDynamicStatus(uid: int, debug=0) -> T.Optional[Resp]:
    cards_data = await getCards(uid)

    last_dynamic = LAST.setdefault(uid, cards_data[0]['desc']['dynamic_id'])

    for i, card_data in enumerate(cards_data):
        if last_dynamic == card_data['desc']['dynamic_id']:
            break
    else:  # 没有找到上次动态，可能为程序初次运行或动态被删除
        LAST[uid] = cards_data[0]['desc']['dynamic_id']
        return None

    if debug:
        i = debug

    if i >= 1:
        LAST[uid] = cards_data[i - 1]['desc']['dynamic_id']
        return CardData(cards_data[i - 1]).resolve()
    else:
        return None  # 没有新动态


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

    def resolve(self) -> Resp:
        name = self["desc"]["user_profile"]["info"]["uname"]
        type = self['desc']['type']

        msg, imgs = Card(self['card'], name, type).resolve()
        return Resp(msg, imgs, self['desc']['dynamic_id'])


def deep_decode(j: T.Union[dict, str]):
    """将str完全解析为json"""
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
    # 还可以按照c_type分为不同的子类，但是摸了
    def __init__(self, obj, name: str, c_type: int):
        super(Card, self).__init__(obj)
        self.name = name
        self.c_type = c_type
        if c_type in [1, 4]:
            self.content = self['item'].get('content')
        elif c_type == 2:
            self.description = self['item'].get('description')
        elif c_type == 8:
            self.dynamic = self.get('dynamic')
            self.title = self.get('title')
            self.pic = self.get('pic')
        elif c_type == 64:
            self.dynamic = self.get('dynamic', '')
            self.title = self.get('title')
            self.banner_url = self.get('banner_url')
        elif c_type == 4200:
            self.roomid = self.get('roomid')
            self.cover = self.get('user_cover') or self.get('cover')
            self.title = self.get('title')

    def resolve(self) -> T.Tuple[str, T.List[str]]:
        try:
            if self.c_type == 1:  # 转发
                msg = f'(转发){self.name}：{self.content}\n{"=" * 20}\n'

                origin_type = self['item']['orig_type']
                if origin_type == 1024:  # 被删了
                    msg_a, img_urls_a = self['item']['tips'], []
                else:  # 没有被删
                    origin_name = self['origin_user']['info']['uname']
                    msg_a, img_urls_a = Card(self['origin'], origin_name, origin_type).resolve()
                msg += msg_a
                img_urls = img_urls_a
            elif self.c_type == 2:  # 图片动态
                msg = f'(动态){self.name}：\n{self.description}\n'
                img_urls = [pic_info['img_src'] for pic_info in self['item']['pictures']]
            elif self.c_type == 4:  # 文字动态
                msg = f'(动态){self.name}：\n{self.content}'
                img_urls = []
            elif self.c_type == 8:  # 视频动态
                msg = f'(视频){self.name}：《{self.title}》\n{self.dynamic}'
                img_urls = [self.pic]
            elif self.c_type == 64:  # 专栏动态
                msg = f'(专栏){self.name}：《{self.title}》\n{self.dynamic}'
                img_urls = [self.banner_url]
            elif self.c_type == 2048:  # 头像框动态
                msg = f'{self.name}：(头像框动态)'
                img_urls = []
            elif self.c_type == 4200:  # 直播间动态
                msg = f'(直播){self.name}：{self.title} https://live.bilibili.com/{self.roomid}'
                img_urls = [self.cover]
            else:  # 未知
                msg = f'{self.name}：(未知动态类型{self.c_type})'
                img_urls = []
        except (TypeError, KeyError):
            msg = f'{self.name}：(动态类型{self.c_type}，解析失败)'
            img_urls = []
        return msg, img_urls
