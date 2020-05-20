import re
from typing import List
from mirai import Group, Member, GroupMessage
from mirai.logger import Event
from .register import Target, Database, Platform
from ..app import app

command_pattern = re.compile(r'动态监控')
add_pattern = re.compile(r'新增|增|添|加')
del_pattern = re.compile(r'取消|删|减|除')

bili_pattern = re.compile(r'space.bilibili.com/(\d+)')


class Command:
    @staticmethod
    async def add(message: GroupMessage, *uid_list: int):
        group_id = message.sender.group.id
        names = Database.add(*[await Target.init(uid, Platform.bili, group_id) for uid in uid_list])
        Event.info(f'群{message.sender.group.name}增加动态监控：{",".join(names)}')
        await app.sendGroupMessage(group=message.sender.group,
                                   message=f'增加动态监控：{",".join(names)}',
                                   quoteSource=message.messageChain.getSource())

    @staticmethod
    async def remove(message: GroupMessage, *uid_list: int):
        group_id = message.sender.group.id
        names = Database.remove(*[await Target.init(uid, Platform.bili, group_id) for uid in uid_list])
        Event.info(f'群{message.sender.group.name}移除动态监控：{",".join(names)}')
        await app.sendGroupMessage(group=message.sender.group,
                                   message=f'移除动态监控：{",".join(names)}',
                                   quoteSource=message.messageChain.getSource())


@app.receiver("GroupMessage")
async def GMHandler(group: Group, member: Member, message: GroupMessage):
    match = command_pattern.search(message.toString())
    command = Command.add if add_pattern.search(message.toString()) \
        else Command.remove if del_pattern.search(message.toString()) \
        else None
    if match and command and bili_pattern.search(message.toString()):
        uid_list: List[int] = bili_pattern.findall(message.toString())
        try:
            await command(message, *uid_list)
        except Exception as e:
            Event.error(e)
