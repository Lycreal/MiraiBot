from enum import Enum
from .channels import *


class ChannelTypes(Enum):
    bili_live = BiliChannel
    youtube_live = YoutubeChannel
    cc_live = NetEaseChannel
