"""
查找B限
显示当前进行中的B限
命令：B限 b限
"""

from mirai import Mirai, Group, GroupMessage, MessageChain

from .run import do_search

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


@sub_app.receiver(GroupMessage)
async def find_living(app: Mirai, group: Group, message: MessageChain):
    if message.toString() in ['b限', 'B限', '.b']:
        m: str = await do_search()
        if m:
            msg = '当前进行中的B限：\n' + m
        else:
            msg = '无进行中的B限'
        await app.sendGroupMessage(group, msg)
