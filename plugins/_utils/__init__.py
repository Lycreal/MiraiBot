from mirai import (
    Mirai, Member, Friend,
    MessageChain, At
)
from typing import Optional, Union

from .alias import MESSAGE_T

# https://mirai-py.originpages.com/tutorial/annotations.html
Sender = Union[Member, Friend]
Type = str


def at_me(app: Mirai, message: MessageChain):
    at: Optional[At] = message.getFirstComponent(At)
    if at:
        return at.target == app.qq
    else:
        return False


def reply(app: Mirai, sender: "Sender", event_type: "Type"):
    async def wrapper(message: MESSAGE_T, *, at_sender: bool = False):
        if at_sender:
            if isinstance(message, list):
                message.insert(0, At(sender.id))
            elif isinstance(message, MessageChain):
                message.__root__.insert(0, At(sender.id))
            else:
                raise TypeError(f"not supported type for reply: {message.__class__.__name__}")
        if event_type == "GroupMessage":
            await app.sendGroupMessage(sender.group, message)
        elif event_type == "FriendMessage":
            await app.sendFriendMessage(sender, message)
        else:
            raise ValueError("Not supported event type")

    return wrapper
