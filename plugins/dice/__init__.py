from mirai import Mirai, Group, GroupMessage, Member, Plain, At
from mirai.event.message.chain import Source
import random
import re

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


def roll(sides):
    return random.randint(1, sides)


@sub_app.receiver(GroupMessage)
async def dice(app: Mirai, group: Group, message: GroupMessage):
    if 'roll' in message.toString():
        sender: Member = message.sender
        group: Group = message.sender.group
        source: Source = message.messageChain.getSource()
        throw = message.toString().strip().lstrip("roll")
        pattern = re.compile(r'\s*((?P<count>[0-9]*)\s*([dD]))?\s*(?P<sides>[0-9]+)')
        match = re.match(pattern, throw)
        if match:
            count = int(match.group('count')) if match.group('count') else 1
            sides = int(match.group('sides'))
            result = 0
            if count > 1:
                for i in range(count):
                    result += roll(sides)
            if count == 1:
                result = roll(sides)
            response = "投掷: %sd%s = %s" % (count, sides, result)
            await app.sendGroupMessage(group, [At(sender.id), Plain(response)], source)
        else:
            help_msg = "未识别的指令 \n格式：roll [投掷次数](可选) d(可选) [骰子面数 或 随机数范围] \n示例：roll 1d6 / roll d100 / roll 50"
            await app.sendGroupMessage(group, [Plain(help_msg)], source)
