import typing as T

from mirai import MessageChain
from mirai.image import InternalImage
from mirai.event.message.base import BaseMessageComponent

MESSAGE_T = T.Union[
    MessageChain,
    BaseMessageComponent,
    T.List[T.Union[BaseMessageComponent, InternalImage]],
    str
]
