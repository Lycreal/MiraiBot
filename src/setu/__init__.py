import re
import asyncio
import random
from typing import List
from PIL import UnidentifiedImageError
from mirai import Group, Member, GroupMessage, Image, Plain
from mirai.logger import Event
from mirai.event.message.chain import Source
from .SetuData import SetuData, SetuResp, SetuDatabase
from .utils import CoolDown, shuzi2number
from ..app import app

cd = CoolDown(app='setu', td=20)


@app.receiver("GroupMessage")
async def GMHandler(group: Group, member: Member, message: GroupMessage):
    match = re.match(r'(?:.*?([\d一二两三四五六七八九十]*)张|来点)?(.{0,10}?)的?色图$', message.toString())
    if match:
        number = shuzi2number(match[1])
        keyword = match[2]
        try:
            await setuExecutor(message, number, keyword)
        except Exception as e:
            Event.warn(repr(e))
    elif message.toString() == '色图配额':
        await checkQuota(message)


async def checkQuota(message: GroupMessage):
    resp = await SetuResp.get('色图配额')
    await app.sendGroupMessage(group=message.sender.group,
                               message=f'剩余配额：{resp.quota}\n恢复时间：{resp.time_to_recover.strftime("%m-%d %H:%M")}',
                               quoteSource=message.messageChain.getSource())


async def setuExecutor(message: GroupMessage, number: int, keyword: str):
    """根据关键词获取data_array，并调用sendSetu"""
    member_id: int = message.sender.id
    if keyword == '':
        resp: SetuResp = SetuResp(code=-430, msg='空关键词')
    elif cd.check(member_id):
        resp: SetuResp = await SetuResp.get(keyword)
    else:
        resp: SetuResp = SetuResp(code=-3, msg='你的请求太快了，休息一下吧')

    if resp.code == 0:
        cd.update(member_id)
        await sendSetu(message, resp.data, number)
    elif resp.code in [429, -430]:
        db = SetuDatabase.load_from_file()
        await sendSetu(message, db.__root__, number)
    else:
        group: Group = message.sender.group
        source: Source = message.messageChain.getSource()
        await app.sendGroupMessage(group, resp.msg, source)


async def sendSetu(message: GroupMessage, data_array: List[SetuData], number: int):
    """发送data_array"""
    group: Group = message.sender.group
    source: Source = message.messageChain.getSource()

    async def send(_prefix: str, _data: SetuData):
        try:
            setu_b: bytes = await _data.get(check_size=False)
            await app.sendGroupMessage(group, [Plain(_prefix), Plain(_data.purl), Image.fromBytes(setu_b)], source)
            Event.info(f"{_prefix}色图已发送，标签：{','.join(_data.tags)}")
        except (asyncio.TimeoutError, UnidentifiedImageError, ValueError) as e:
            Event.warn(e)

    number = min(number, len(data_array))

    tasks: List[asyncio.Task] = []
    for i, data in enumerate(random.sample(data_array, k=number)):
        prefix = f'[{i}/{number}]' if number > 1 else ''
        task = asyncio.create_task(send(prefix, data))
        tasks.append(task)
        await asyncio.sleep(5)
    done, pending = await asyncio.wait(tasks, timeout=10)
    if pending:
        [t.cancel() for t in pending]
        msg = f'共{number}个任务，{len(done)}个完成，{len(pending)}个超时'
        await app.sendGroupMessage(group, msg, source)
