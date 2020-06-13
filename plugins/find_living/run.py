import aiohttp
import asyncio
import math
import re
from typing import Dict, List
from dataclasses import dataclass

# https://github.com/lovelyyoshino/Bilibili-Live-API/blob/master/API.getRoomList.md
API_URL = 'https://api.live.bilibili.com/room/v3/area/getRoomList'


@dataclass
class Room:
    roomid: int
    uid: int
    title: str
    uname: str
    online: int

    def __init__(self, roomid, uid, title, uname, online, **_):
        self.roomid = roomid
        self.uid = uid
        self.title = title
        self.uname = uname
        self.online = online


def params(page, page_size=99):
    return {
        'area_id': 199,
        'page_size': page_size,
        'page': page + 1,
        'sort_type': 'online'
    }


async def do_search_once(page: int):
    async with aiohttp.request('GET', API_URL, params=params(page)) as f:
        data_json = await f.json(encoding='utf8')
    count = data_json['data']['count']
    living_list: List[Dict] = data_json['data']['list']
    room_list = [Room(**room) for room in living_list]
    return room_list, count


async def do_search():
    room_list, count = await do_search_once(0)

    tasks = [do_search_once(i) for i in range(1, math.ceil(count / 99))]
    [room_list.extend(r[0]) for r in await asyncio.gather(*tasks)]
    # for task in asyncio.as_completed(tasks):
    #     room_list += (await task)[0]

    return '\n'.join([f'{r.uname}: {r.title}' for r in room_list if re.search(r'[bB].*限', r.title)])
