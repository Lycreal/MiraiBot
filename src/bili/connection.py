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
    else:
        LAST[uid] = cards_data[0]['desc']['dynamic_id']
        return  # 没有找到上次动态，可能为初次运行或被删除

    if debug:
        i = debug

    if i >= 1:
        LAST[uid] = cards_data[i - 1]['desc']['dynamic_id']
        card = Card(Card.deep_decode(cards_data[i - 1]))
        return card.toString()
    else:
        return ''  # 没有新动态


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


class Card(dict):
    @staticmethod
    def deep_decode(j: T.Union[dict, str]):
        if isinstance(j, dict):
            for k, v in j.items():
                j[k] = Card.deep_decode(v)
        elif isinstance(j, str):
            try:
                j = Card.deep_decode(json.loads(j))
            except json.decoder.JSONDecodeError:
                pass
        return j

    @property
    def name(self) -> str:
        return self["desc"]["user_profile"]["info"]["uname"]

    def toString(self) -> str:
        # https://github.com/wxz97121/QQBot_bilibili/blob/master/VRBot_github.py
        try:
            if self['desc']['type'] == 64:
                msg = '{}发了新专栏「{}」：{}'.format(
                    self.name,
                    self['card']['title'],
                    self['card']['dynamic'])
            else:
                if self['desc']['type'] == 8:
                    msg = '{}发了新视频「{}」：{}'.format(
                        self.name,
                        self['card']['title'],
                        self['card']['dynamic'])
                else:
                    if 'description' in self['card']['item']:
                        # 这个是带图新动态
                        imgs = \
                            [f"[CQ:image,file={pic_info['img_src']}]" for pic_info in self['card']['item']['pictures']]
                        msg = '{}发了新动态：{}{}'.format(
                            self.name,
                            self['card']['item']['description'],
                            ''.join(imgs))
                        # CQ使用参考：[CQ:image,file=http://i1.piimg.com/567571/fdd6e7b6d93f1ef0.jpg]
                    else:
                        # 这个表示转发，原动态的信息在 cards-item-origin里面。里面又是一个超级长的字符串……
                        # origin = json.loads(self['card']['item']['origin'],encoding='gb2312') 我也不知道这能不能解析，没试过
                        # origin_name = 'Fuck'
                        if 'origin_user' in self['card']:
                            msg = '{}转发了「{}」的动态：{}'.format(
                                self.name,
                                self['card']['origin_user']['info']['uname'],
                                self['card']['item']['content'])

                        else:
                            # 这个是不带图的自己发的动态
                            msg = '{}发了新动态：{}'.format(
                                self.name,
                                self['card']['item']['content'])

            msg += f"\n本条动态地址为: https://t.bilibili.com/{self['desc']['dynamic_id']}"
        except (TypeError, KeyError) as e:
            raise e
        return msg
