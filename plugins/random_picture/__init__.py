from mirai import (
    Mirai, GroupMessage, FriendMessage,
    MessageChain,
    Image
)
from mirai.logger import Event as EventLogger

from .sources import CatPicture, MoePicture
from .._utils import at_me, reply, Sender, Type

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")

sources = {
    'cat': CatPicture(),
    'moe': MoePicture()
}


@sub_app.receiver(FriendMessage)
@sub_app.receiver(GroupMessage)
async def GMHandler(app: Mirai, sender: "Sender", event_type: "Type", message: MessageChain):
    app_reply = reply(app, sender, event_type)
    for tag, source in sources.items():
        keywords = source.keywords
        text = message.toString()
        if (text in keywords) or (at_me(app, message) and any(keyword in text for keyword in keywords)):
            EventLogger.info(f'随机图片{tag}：请求者{sender.id}')
            try:
                image_url = await source.get()
                await app_reply([await Image.fromRemote(image_url)], at_sender=True)
            except Exception as e:
                import traceback
                EventLogger.error(e)
                EventLogger.error(traceback.format_exc())
            break
