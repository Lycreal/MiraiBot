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
                    resp = await GetDynamicStatus(target.uid)
                except Exception as e:
                    Event.error(e)
                    continue
                if resp:
                    footer = f"\n\n本条动态的地址为: https://t.bilibili.com/{resp.dynamic_id}"
                    Event.info(f'{target.name}动态更新：{footer}')
                    components = [Plain(resp.msg)] + \
                                 [await Image.fromRemote(url) for url in resp.imgs] + \
                                 [Plain(footer)]
                    for group_id in target.groups:
                        await app.sendGroupMessage(group=group_id, message=components)
