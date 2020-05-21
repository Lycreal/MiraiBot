import re
import typing as T
from mirai import Group, Member, GroupMessage
from mirai.logger import Event
from .register import Target, Database, Platform
from ..app import app


class Command:
    @classmethod
    def getCommand(cls, msg: str):
        command_pattern = re.compile(r'动态监控')
        cmd_table: T.Dict[T.Callable[[GroupMessage, T.Tuple[int, ...]], T.Coroutine], T.Pattern[str]] = {
            cls.add: re.compile(r'新增|增|添|加'),
            cls.remove: re.compile(r'取消|删|减|除'),
            cls.show: re.compile(r'显示|列表')
        }
        if not command_pattern.search(msg):
            return None
        for cmd, pattern in cmd_table.items():
            if pattern.search(msg):
                Event.info(f'Handled 「{msg}」as a command')
                return cmd
        else:
            return None

    @staticmethod
    async def add(message: GroupMessage, *uid_list: int):
        group_id = message.sender.group.id
        names = Database.add(*[await Target.init(uid, Platform.bili, group_id) for uid in uid_list])
        Event.info(f'群「{message.sender.group.name}」增加动态监控：{",".join(names)}')
        await app.sendGroupMessage(group=message.sender.group,
                                   message=f'增加动态监控：{",".join(names)}',
                                   quoteSource=message.messageChain.getSource())

    @staticmethod
    async def remove(message: GroupMessage, *uid_list: int):
        group_id = message.sender.group.id
        names = Database.remove(*[await Target.init(uid, Platform.bili, group_id) for uid in uid_list])
        Event.info(f'群「{message.sender.group.name}」移除动态监控：{",".join(names)}')
        await app.sendGroupMessage(group=message.sender.group,
                                   message=f'移除动态监控：{",".join(names)}',
                                   quoteSource=message.messageChain.getSource())

    @staticmethod
    async def show(message: GroupMessage, *uid_list: int):
        group_id = message.sender.group.id
        names = Database.show(group_id)
        msg = '动态监控列表：\n{}'.format('\n'.join(names)) if names else '动态监控列表为空'
        Event.info(f'群「{message.sender.group.name}」{msg}')
        await app.sendGroupMessage(group=message.sender.group,
                                   message=msg,
                                   quoteSource=message.messageChain.getSource())


@app.receiver("GroupMessage")
async def GMHandler(group: Group, member: Member, message: GroupMessage):
    command = Command.getCommand(message.toString())
    bili_pattern = re.compile(r'space.bilibili.com/(\d+)')
    if command:
        uid_list: T.List[int] = bili_pattern.findall(message.toString())
        try:
            await command(message, *uid_list)
        except Exception as e:
            Event.error(e)
