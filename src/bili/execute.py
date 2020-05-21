import asyncio
import re
import typing as T
from mirai import Plain, Image
from mirai.image import InternalImage
from mirai.event.message.components import BaseMessageComponent
from mirai.logger import Event
from .register import Database
from .connection import GetDynamicStatus
from ..app import app


async def str2Components(msg: str) -> T.List[T.Union[BaseMessageComponent, InternalImage]]:
    img_pattern = re.compile(r'\[CQ:image,file=(.*)\]')
    img_array: T.List[InternalImage] = []
    for match in img_pattern.finditer(msg):
        msg.replace(match[0], '')
        img_array.append(await Image.fromRemote(match[1]))
    return [Plain(msg)] + img_array


async def execute(delay: float):
    while True:
        for target in Database.load().__root__:
            if target.groups:
                try:
                    await asyncio.sleep(delay)
                    msg = await GetDynamicStatus(target.uid)
                    Event.info(f'已查询{target.name}，信息：{msg}')
                except Exception as e:
                    Event.error(e)
                    continue
                if msg:
                    components = await str2Components(msg)
                    for group_id in target.groups:
                        await app.sendGroupMessage(group=group_id, message=components)
