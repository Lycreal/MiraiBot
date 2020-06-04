import typing as T
from mirai import (
    Mirai, Group,
    GroupMessage,
    MessageChain, Source, Quote, Plain
)

from mirai.exceptions import UnknownReceiverTarget

from .._utils.alias import MESSAGE_T

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


@sub_app.receiver(GroupMessage)
async def recall(app: Mirai, group: Group, message: MessageChain, source: Source):
    def reply(msg: MESSAGE_T, at: bool = False):
        _s = source if at else None
        return app.sendGroupMessage(group, msg, _s)

    plain: Plain
    if any(plain.text.strip() == '撤回' for plain in message.getAllofComponent(Plain)):
        quote: T.Optional[Quote] = message.getFirstComponent(Quote)
        if quote:
            try:
                await app.revokeMessage(quote.id)
                await app.revokeMessage(source.id)
            except UnknownReceiverTarget as e:
                if quote.senderId == app.qq:
                    await reply(str(e), at=True)
            except PermissionError:
                pass
