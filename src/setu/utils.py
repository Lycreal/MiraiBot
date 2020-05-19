import typing as T
from datetime import datetime, timedelta
from pydantic import BaseModel


class CoolDown(BaseModel):
    value: T.Dict[int, datetime] = {}
    app: str
    td: float

    def update(self, mid: int):
        self.value.update({mid: datetime.now()})

    def check(self, mid: int):
        ret = datetime.now() - self.value.get(mid, datetime.utcfromtimestamp(0)) >= timedelta(seconds=self.td)
        return ret


def shuzi2number(shuzi: str):
    s = {'一': 1, '两': 2, '二': 2, '三': 3,
         '四': 4, '五': 5, '六': 6, '七': 7,
         '八': 8, '九': 9, '十': 10}
    if not shuzi:
        return 1
    elif shuzi in s.keys():
        return s[shuzi]
    elif shuzi.isdecimal():
        return int(shuzi)
    else:
        return 1
