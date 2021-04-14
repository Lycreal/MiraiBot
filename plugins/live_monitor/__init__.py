"""直播监控

使用方法：
直播监控添加 <频道1> <频道2> ...
直播监控移除 <频道1> <频道2> ...
直播监控列表 [页码]
直播监控详细列表 [页码]

详细说明：https://github.com/Lycreal/MiraiBot/blob/master/plugins/live_monitor/README.md
"""

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
    @classmethod
    def getCommand(cls, msg: str) -> T.Optional[T.Callable[[Group, str], T.Coroutine[T.Any, T.Any, str]]]:
        if '直播' in msg and '监控' in msg:
            command_map = {
                re.compile(r'新增|增|添|加'): cls.add,
                re.compile(r'取消|删|减|除'): cls.remove,
                re.compile(r'显示|列表'): cls.show
            }
            for pattern in command_map.keys():
                if pattern.search(msg):
                    return command_map[pattern]
            else:
                return cls.help
        return None

    @staticmethod
    async def add(group: Group, msg: str):
        matches: T.Dict[ChannelTypes, T.List[str]] = {
            ChannelTypes.bili_live: re.compile(r'live.bilibili.com/(\d+)').findall(msg),
            ChannelTypes.youtube_live: re.compile(r'UC[\w-]{22}').findall(msg),
            ChannelTypes.cc_live: re.compile(r'cc.163.com/(\d+)').findall(msg)
        }
        count = [
            monitors[channel_type].add(cid, group.id)
            for channel_type, cids in matches.items()
            for cid in cids
        ].count(True)
        return f'已添加{count}个频道'

    @staticmethod
    async def remove(group: Group, msg: str):
        matches: T.Dict[ChannelTypes, T.List[str]] = {
            ChannelTypes.bili_live: re.compile(r'live.bilibili.com/(\d+)').findall(msg),
            ChannelTypes.youtube_live: re.compile(r'UC[\w-]{22}').findall(msg),
            ChannelTypes.cc_live: re.compile(r'cc.163.com/(\d+)').findall(msg)
        }
        count = [
            monitors[channel_type].remove(cid, group.id)
            for channel_type, cids in matches.items()
            for cid in cids + msg.split()
        ].count(True)
        return f'已移除{count}个频道'

    @staticmethod
    async def show(group: Group, msg: str):
        page = int(msg.split()[-1]) - 1 if msg.split()[-1].isdecimal() else 0
        page_size = 10
        channel_names = [(channel_type, target.name, target.id)
                         for channel_type in monitors.keys()
                         for target in monitors[channel_type].database.__root__
                         if group.id in target.groups
                         ]
        page_total = len(channel_names) // page_size + bool(len(channel_names) % page_size)
        ret = f'直播监控列表：第{page + 1}页/共{page_total}页\n'

        tmp: T.Dict[ChannelTypes, T.List[str]] = {}
        for channel_type, name, tid in channel_names[page_size * page:page_size * (page + 1)]:
            tmp.setdefault(channel_type, []).append(
                f'{name}\t{tid}' if '详细' in msg else (name or tid)
            )
        for channel_type, names in tmp.items():
            ret += '[{}]\n{}\n'.format(
                channel_type.name,
                '\n'.join(names)
            )
        return ret

    # noinspection PyUnusedLocal
    @staticmethod
    async def help(group: Group, msg: str):
        return __doc__.strip()


@sub_app.receiver(GroupMessage)
async def GMHandler(app: Mirai, group: Group, message: MessageChain):
    command = Command.getCommand(message.toString())
    if command:
        try:
            msg = await command(group, message.toString())
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
        EventLogger.warning(e)
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
sub_app.subroutine(wrapper(ChannelTypes.bili_live, 10))
sub_app.subroutine(wrapper(ChannelTypes.youtube_live, 20))
sub_app.subroutine(wrapper(ChannelTypes.cc_live, 30))
