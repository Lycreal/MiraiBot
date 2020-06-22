import re
import asyncio
import traceback
import typing as T

from mirai import Mirai, Group, MessageChain, GroupMessage, Plain, Image
from mirai.logger import Event as EventLogger

from .monitor import Monitor
from .channels import ChannelResolveError
from .enums import ChannelTypes

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


class Command:
    cmd_T = T.Callable[
        [Group, T.Dict[ChannelTypes, T.List[str]]], T.Coroutine[T.Any, T.Any, str]]

    @classmethod
    def getCommand(cls, msg: str) -> T.Tuple[T.Optional[cmd_T], T.Dict[ChannelTypes, T.List[str]]]:
        COMMAND = '直播' in msg and '监控' in msg
        commands = {
            cls.add: re.compile(r'新增|增|添|加').search(msg),
            cls.remove: re.compile(r'取消|删|减|除').search(msg),
            cls.show_detail: re.compile(r'显示|列表').search(msg)
        }
        if COMMAND:
            for command, match in commands.items():
                if match:
                    break
            else:
                command = cls.add
        else:
            command = None
            msg = ''

        matches: T.Dict[ChannelTypes, T.List[str]] = {
            ChannelTypes.bili_live: re.compile(r'live.bilibili.com/(\d+)').findall(msg),
            ChannelTypes.youtube_live: re.compile(r'UC[\w-]{22}').findall(msg),
            ChannelTypes.cc_live: re.compile(r'cc.163.com/(\d+)').findall(msg)
        }
        if command == cls.add and all(len(match) == 0 for match in matches.values()):
            command = cls.show
        elif command == cls.remove:
            for cids in matches.values():
                cids.extend(msg.split())
        return command, matches

    @staticmethod
    async def add(group: Group, matches: T.Dict[ChannelTypes, T.List[str]]):
        count = [
            monitors[channel_type].add(cid, group.id)
            for channel_type, cids in matches.items()
            for cid in cids
        ].count(True)
        return f'已添加{count}个频道'

    @staticmethod
    async def remove(group: Group, matches: T.Dict[ChannelTypes, T.List[str]]):
        count = [
            monitors[channel_type].remove(cid, group.id)
            for channel_type, cids in matches.items()
            for cid in cids
        ].count(True)
        return f'已移除{count}个频道'

    @staticmethod
    async def show(group: Group, matches: T.Dict[ChannelTypes, T.List[str]]):
        ret = '当前直播监控列表：\n'
        for channel_type in matches.keys():
            tmp = '\n'.join([target.name or target.id
                             for target in monitors[channel_type].database.__root__
                             if group.id in target.groups])
            if tmp:
                ret += f'[{channel_type.name}]\n{tmp}\n'
        return ret

    @staticmethod
    async def show_detail(group: Group, matches: T.Dict[ChannelTypes, T.List[str]]):
        ret = '当前直播监控列表：\n'
        for channel_type in matches.keys():
            tmp = '\n'.join([f'{target.name} {target.id}'.strip()
                             for target in monitors[channel_type].database.__root__
                             if group.id in target.groups])
            if tmp:
                ret += f'[{channel_type.name}]\n{tmp}\n'
        return ret


@sub_app.receiver(GroupMessage)
async def GMHandler(app: Mirai, group: Group, message: MessageChain):
    command, matches = Command.getCommand(message.toString())
    if command:
        try:
            msg = await command(group, matches)
            await app.sendGroupMessage(group, msg.strip())
        except Exception as e:
            EventLogger.error(e)
            EventLogger.error(traceback.format_exc())


def wrapper(channel_type: ChannelTypes, duration: float):
    async def exec_wrapper(app: Mirai):
        monitor = monitors[channel_type]
        while True:
            await asyncio.sleep(duration)
            if not app.enabled:
                pass
            asyncio.create_task(execute(app, monitor))

    return exec_wrapper


async def execute(app: Mirai, monitor: Monitor) -> None:
    # noinspection PyBroadException
    try:
        resp, groups = await monitor.run()
        if resp:
            EventLogger.info(f'{resp.name}直播：{resp.url}')

            if resp.cover:
                cover: Image = await app.uploadImage("group", await Image.fromRemote(resp.cover))
                components = [Plain(f'(直播){resp.name}: {resp.title}\n{resp.url}\n'), cover]
            else:
                components = [Plain(f'(直播){resp.name}: {resp.title}\n{resp.url}')]

            tasks = [asyncio.create_task(
                app.sendGroupMessage(group=group_id, message=components)
            ) for group_id in groups]

            done, pending = await asyncio.wait(tasks)
            for task in done:
                if e := task.exception():
                    EventLogger.error(e)

    except ChannelResolveError as e:
        EventLogger.error(e)
    except Exception:
        EventLogger.error(traceback.format_exc())


monitors: T.Dict[ChannelTypes, Monitor] = {
    channel_type: Monitor(channel_type)
    for channel_type in [
        ChannelTypes.bili_live,
        ChannelTypes.youtube_live,
        ChannelTypes.cc_live
    ]
}
sub_app.subroutine(wrapper(ChannelTypes.bili_live, 5))
sub_app.subroutine(wrapper(ChannelTypes.youtube_live, 20))
sub_app.subroutine(wrapper(ChannelTypes.cc_live, 30))
