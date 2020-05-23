import re
import asyncio
import traceback
import typing as T

from mirai import Mirai, GroupMessage, Plain, Image
from mirai.logger import Event as EventLogger

from .register import Target, Database, Platform
from .connection import getDynamicStatus

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


class Command:
    cmd_T = T.Callable[[Mirai, GroupMessage, T.Tuple[int]], T.Coroutine[T.Any, T.Any, None]]

    @classmethod
    def getCommand(cls, msg: str) -> T.Tuple[T.Optional[cmd_T], T.List[int]]:
        COMMAND = re.compile(r'动态监控').search(msg)
        ADD = re.compile(r'新增|增|添|加').search(msg)
        RM = re.compile(r'取消|删|减|除').search(msg)
        SHOW = re.compile(r'显示|列表').search(msg)
        uid_list = re.compile(r'space.bilibili.com/(\d+)').findall(msg)
        if not COMMAND:
            return None, uid_list
        elif not uid_list:
            return cls.show, uid_list
        elif ADD:
            return cls.add, uid_list
        elif RM:
            return cls.remove, uid_list
        elif SHOW:
            return cls.show, uid_list
        else:
            return cls.show, uid_list

    @staticmethod
    async def add(app: Mirai, message: GroupMessage, *uid_list: int):
        group_id = message.sender.group.id
        names = Database.add(*[await Target.init(uid, Platform.bili, group_id) for uid in uid_list])
        EventLogger.info(f'群「{message.sender.group.name}」增加动态监控：{",".join(names)}')
        await app.sendGroupMessage(group=message.sender.group,
                                   message=f'增加动态监控：{",".join(names)}',
                                   quoteSource=message.messageChain.getSource())

    @staticmethod
    async def remove(app: Mirai, message: GroupMessage, *uid_list: int):
        group_id = message.sender.group.id
        names = Database.remove(*[await Target.init(uid, Platform.bili, group_id) for uid in uid_list])
        EventLogger.info(f'群「{message.sender.group.name}」移除动态监控：{",".join(names)}')
        await app.sendGroupMessage(group=message.sender.group,
                                   message=f'移除动态监控：{",".join(names)}',
                                   quoteSource=message.messageChain.getSource())

    @staticmethod
    async def show(app: Mirai, message: GroupMessage, *uid_list: int):
        group_id = message.sender.group.id
        names = Database.show(group_id)
        msg = '动态监控列表：\n{}'.format('\n'.join(names)) if names else '动态监控列表为空'
        EventLogger.info(f'群「{message.sender.group.name}」{msg}')
        await app.sendGroupMessage(group=message.sender.group,
                                   message=msg,
                                   quoteSource=message.messageChain.getSource())


@sub_app.receiver("GroupMessage")
async def GMHandler(app: Mirai, message: GroupMessage):
    command, uid_list = Command.getCommand(message.toString())
    if command:
        try:
            await command(app, message, *uid_list)
        except Exception as e:
            EventLogger.error(e)


@sub_app.subroutine
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
                    resp = await getDynamicStatus(target.uid)
                    EventLogger.info(f'动态检查：{target.name}')
                except Exception as e:
                    EventLogger.error(e)
                    traceback.print_exc()
                    continue
                if resp:
                    footer = f"\n\n本条动态的地址为: https://t.bilibili.com/{resp.dynamic_id}"
                    EventLogger.info(f'{target.name}动态更新：https://t.bilibili.com/{resp.dynamic_id}')
                    # noinspection PyTypeChecker,PydanticTypeChecker
                    components = [Plain(resp.msg)] + \
                                 [await Image.fromRemote(url) for url in resp.imgs] + \
                                 [Plain(footer)]
                    for group_id in target.groups:
                        await app.sendGroupMessage(group=group_id, message=components)
