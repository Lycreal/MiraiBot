import asyncio
from mirai import Plain, Image
from mirai.logger import Event
from .register import Database
from .connection import GetDynamicStatus
from ..app import app


async def execute(delay: float):
    while True:
        for target in Database.load().__root__:
            if target.groups:
                try:
                    await asyncio.sleep(delay)
                    msg, imgs = await GetDynamicStatus(target.uid)
                except Exception as e:
                    Event.error(e)
                    continue
                if msg:
                    Event.info(f'{target.name}动态更新：{msg}')
                    components = [Plain(msg)] + [await Image.fromRemote(url) for url in imgs]
                    for group_id in target.groups:
                        await app.sendGroupMessage(group=group_id, message=components)
