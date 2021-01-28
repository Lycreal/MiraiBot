import typing as T
import aiohttp
from mirai import Mirai, Group, GroupMessage, MessageChain, Image, Plain
from io import BytesIO
from PIL import Image as im
from PIL import ImageSequence

sub_app = Mirai(f"mirai://localhost:8080/?authKey=0&qq=0")


@sub_app.receiver(GroupMessage)
async def minimize(app: Mirai, group: Group, message: MessageChain):
    if '变小' in message.toString() or 'mini' in message.toString():
        threshold = [int(s) for s in message.toString().split() if s.isdigit()] or [48, 24, 10]
        image: T.Optional[Image] = message.getFirstComponent(Image)
        if image and image.url:
            async with aiohttp.request('GET', image.url) as resp:
                img = im.open(BytesIO(await resp.read()))

            width, height = img.size
            if min(width, height) < min(threshold):
                help_msg = "指令错误 \n格式：mini [自定义边长限制](可选) [图片] 或 变小 [自定义边长限制](可选) [图片] \n图片尺寸不得小于边长限制（默认10像素）"
                await app.sendGroupMessage(group, [Plain(help_msg)])
            else:
                img_queue = []
                for limit in threshold:
                    scale = (limit / width if width <= height else limit / height)
                    w, h = int(scale * width), int(scale * height)

                    img_format = img.format
                    if img_format == 'GIF':
                        frames = ImageSequence.Iterator(img)
                        resized = gif_resize(w, h, frames)
                        generated = next(resized)
                        generated.info = img.info
                        buf = BytesIO()
                        tp = 255
                        if 'transparency' in img.info:
                            tp = img.info["transparency"]
                        generated.save(buf, format=img_format, transparency=tp, save_all=True,
                                       append_images=list(resized), loop=0)
                    else:
                        resized = img.resize((w, h), 1)
                        buf = BytesIO()
                        resized.save(buf, format=img_format)

                    img_byte = buf.getvalue()
                    img_queue.append(Image.fromBytes(img_byte))
                await app.sendGroupMessage(group, img_queue)


def gif_resize(w, h, frames):
    for frame in frames:
        resized = frame.copy().resize((w, h), 1)
        yield resized
