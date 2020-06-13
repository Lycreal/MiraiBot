import abc
import difflib
import asyncio
from typing import Optional
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

import aiohttp


@dataclass
class LiveCheckResponse:
    name: str
    live_status: int
    title: str = ''
    url: Optional[str] = None
    cover: Optional[str] = None  # 封面url


class BaseChannel(abc.ABC):
    TIME_PRE = timedelta(minutes=5)
    TIMEZONE = timezone(timedelta(hours=8))

    def __init__(self, cid: str):
        self.cid: str = cid  # 频道id

        self.ch_name: str = ''  # 频道名，初始化时设置，或检查状态时设置

        self.last_live_status: int = 1  # 0 for down, 1 for living
        self.last_check_time: datetime = datetime.fromtimestamp(0, self.TIMEZONE)
        self.last_title: str = ''

    @property
    @abc.abstractmethod
    def api_url(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def resolve(self, html_s: str) -> LiveCheckResponse:
        raise NotImplementedError

    # 播报策略
    def judge(self, response: LiveCheckResponse, strategy: int = 0b011) -> bool:
        """
        判断 response 是否满足开播信号条件

        :param response: LiveCheckResponse
        :param strategy: 1:新开播 2:冷却 4:标题变更
                         三者线性组合
                         0:debug
        :return: bool
        """
        status_changed: bool = response.live_status == 1 and response.live_status != self.last_live_status  # 新开播

        time_delta = datetime.now(self.TIMEZONE) - self.last_check_time  # 距离上次检测到开播状态的时间
        cool_down: bool = time_delta >= timedelta(hours=1)  # 防止短时间内多次提醒

        similarity = difflib.SequenceMatcher(..., response.title, self.last_title).quick_ratio()  # 相似度
        title_changed: bool = self.last_title != '' and similarity < 0.7  # 防止对标题微调进行提醒

        return strategy == 0 or bool(strategy & (0b001 * status_changed | 0b010 * cool_down | 0b100 * title_changed))

    async def update(self, timeout: float = 15, strategy=...) -> Optional[LiveCheckResponse]:
        try:
            async with aiohttp.request('GET', self.api_url, timeout=aiohttp.ClientTimeout(timeout)) as resp:
                html_s = await resp.text(encoding='utf8')
            response = await self.resolve(html_s)
        except (asyncio.TimeoutError, TypeError, IndexError, KeyError, ValueError):
            return None

        judge = self.judge(response, strategy)
        if response.live_status == 1:
            self.last_check_time = datetime.now(self.TIMEZONE)
            self.last_live_status = response.live_status
            self.last_title = response.title
        return response if judge else None

    def __str__(self):
        return self.ch_name or self.cid
