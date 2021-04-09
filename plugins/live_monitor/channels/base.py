import abc
import difflib
import os.path
from typing import Optional
from datetime import datetime, timezone, timedelta

import aiohttp
from pydantic.dataclasses import dataclass


@dataclass
class LiveCheckResponse:
    name: str
    live_status: Optional[int]
    title: str
    url: str
    cover: Optional[str]  # 封面url


class ChannelResolveError(Exception):
    pass


class BaseChannel(abc.ABC):
    TIMEZONE = timezone(timedelta(hours=8))

    def __init__(self, cid: str, name=''):
        self.cid: str = cid  # 频道id

        self.ch_name: str = name  # 频道名，初始化时设置，或检查状态时设置

        self.start_signal: bool = False
        self.start_time: datetime = datetime.fromtimestamp(0, self.TIMEZONE)
        self.start_nicely: bool = True

        self.last_check_status: int = 1  # 0 for down, 1 for living
        self.last_check_living: datetime = datetime.fromtimestamp(0, self.TIMEZONE)
        self.last_judge_title: str = ''

    @property
    @abc.abstractmethod
    def api_url(self):
        raise NotImplementedError

    @abc.abstractmethod
    async def resolve(self, html_s: str) -> LiveCheckResponse:
        raise NotImplementedError

    # 播报策略
    def judge(self, response: LiveCheckResponse, strategies=...) -> bool:
        """
        判断 response 是否满足开播信号条件
        """
        if strategies is ...:
            strategies = [0b0101, 0b1011]

        if response.live_status == 1 != self.last_check_status:  # 新开播
            self.start_signal = True
            self.start_time = datetime.now(self.TIMEZONE)
            self.start_nicely = datetime.now(self.TIMEZONE) - self.last_check_living >= timedelta(hours=1)  # 非连续直播
        if response.live_status == 1:  # 开播中
            self.last_check_living = datetime.now(self.TIMEZONE)
        else:
            self.start_signal = False
        self.last_check_status = response.live_status

        situation = sum(condition << i for i, condition in enumerate([
            # 未提醒的新开播
            self.start_signal,
            # 非连续直播
            self.start_nicely,
            # 标题变化较大
            difflib.SequenceMatcher(None, response.title, self.last_judge_title).quick_ratio() < 0.7,
            # 离最近一次开播2分钟以上
            datetime.now(self.TIMEZONE) - self.start_time >= timedelta(minutes=2)
        ]))

        if any(strategy == strategy & situation for strategy in strategies):
            self.start_signal = False
            self.last_judge_title = response.title
            return True
        else:
            return False

    async def update(self, timeout: float = 15, strategies=...) -> Optional[LiveCheckResponse]:
        try:
            async with aiohttp.request('GET', self.api_url, timeout=aiohttp.ClientTimeout(timeout)) as resp:
                html_s = await resp.text(encoding='utf8')
            response = await self.resolve(html_s)
        except Exception as e:
            file = e.__traceback__.tb_next.tb_frame.f_globals["__file__"]
            lineno = e.__traceback__.tb_next.tb_lineno
            raise ChannelResolveError(
                f'Fetching channel information failed: {self.ch_name or self.cid}\n'
                f' [{os.path.basename(file)}][{lineno}] {e.__class__.__name__}: {str(e)}'
            ) from e

        judge = self.judge(response, strategies)
        return response if judge else None

    def __str__(self):
        return self.ch_name or self.cid
