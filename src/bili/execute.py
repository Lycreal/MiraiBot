import asyncio
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
                    msg = await GetDynamicStatus(target.uid)
                    Event.info(f'已查询{target.name}，信息：{msg}')
                except Exception as e:
                    Event.error(e)
                    continue
                if msg:
                    for group_id in target.groups:
                        await app.sendGroupMessage(group=group_id, message=msg)
