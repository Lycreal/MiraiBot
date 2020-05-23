import asyncio
import traceback
from mirai import Mirai, Plain, Image
from mirai.logger import Event
from .register import Database
from .connection import GetDynamicStatus
from ..app import app


@app.subroutine
async def execute(app: Mirai):
    delay = 10
    while True:
        if not (hasattr(app, 'enabled') and app.enabled):
            await asyncio.sleep(delay)
            continue
        for target in Database.load().__root__:
            if target.groups:
                try:
                    await asyncio.sleep(delay)
                    resp = await GetDynamicStatus(target.uid)
                    Event.info(f'动态检查：{target.name}')
                except Exception as e:
                    Event.error(e)
                    traceback.print_exc()
                    continue
                if resp:
                    footer = f"\n\n本条动态的地址为: https://t.bilibili.com/{resp.dynamic_id}"
                    Event.info(f'{target.name}动态更新：https://t.bilibili.com/{resp.dynamic_id}')
                    components = [Plain(resp.msg)] + \
                                 [await Image.fromRemote(url) for url in resp.imgs] + \
                                 [Plain(footer)]
                    for group_id in target.groups:
                        await app.sendGroupMessage(group=group_id, message=components)
