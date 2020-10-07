import typing as T
from mirai import Mirai, Group, FriendMessage, GroupMessage, MessageChain, Image, Plain
import requests
from io import BytesIO
from PIL import Image as im
import io

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


@sub_app.receiver(GroupMessage)
async def plugin_test(app: Mirai, group: Group, message: MessageChain):
    if '变小' in message.toString() or 'mini' in message.toString():
        image: T.Optional[Image] = message.getFirstComponent(Image)
        if image and image.url:
            threshold = [48, 24, 10]
            response = requests.get(image.url)
            img = im.open(BytesIO(response.content))
            img_format = img.format
            if img_format == 'GIF':
                print('gif')
                await app.sendGroupMessage(group, '不行')
            else:
                width, height = img.size
                if min(width, height) < 25:
                    await app.sendGroupMessage(group, '太小了！')
                else:
                    img_queue = []
                    for limit in threshold:
                        scale = (limit / width if width <= height else limit / height)
                        w, h = int(scale * width), int(scale * height)
                        resized = img.resize((w, h), 1)
                        buf = io.BytesIO()
                        resized.save(buf, format=img_format)
                        img_byte = buf.getvalue()
                        img_queue.append(Image.fromBytes(img_byte))
                    await app.sendGroupMessage(group, img_queue)