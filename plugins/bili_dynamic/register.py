import typing as T
import json
from enum import Enum
from pathlib import Path
from pydantic import BaseModel, ValidationError
import aiohttp

from config import data_path

Path(data_path).mkdir(exist_ok=True)
SAVE_FILE = Path(data_path).joinpath('bili_dynamic.json')


class Platform(Enum):
    bili_dynamic = 'bili_dynamic'


class Target(BaseModel):
    name: str
    uid: int
    platform: Platform
    groups: T.Set[int]

    @classmethod
    async def init(cls, uid: T.Union[int, str], platform: Platform, group_id: int) -> "Target":
        if platform == Platform.bili_dynamic:
            url = f'https://api.bilibili.com/x/space/acc/info?mid={uid}'
            async with aiohttp.request('GET', url) as resp:
                name = (await resp.json(encoding='utf8'))['data']['name']
            return cls(name=name, uid=uid, platform=platform, groups={group_id})
        else:
            raise

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return (self.uid, self.platform) == (other.uid, other.platform)
        else:
            return False

    # def __hash__(self):
    #     return hash((self.uid, self.platform))


class Database(BaseModel):
    __root__: T.List[Target] = []

    @classmethod
    def load(cls) -> "Database":
        try:
            db: Database = cls.parse_file(SAVE_FILE)
        except (FileNotFoundError, json.JSONDecodeError, ValidationError):
            db = cls()
        return db

    def save_to_file(self) -> None:
        with SAVE_FILE.open('w', encoding='utf8') as f:
            json.dump([json.loads(target.json()) for target in self.__root__], f, ensure_ascii=False, indent=2)

    # @classmethod
    # def save(cls, *data_array: Target):
    #     db: cls = cls.load()
    #     for data in data_array:
    #         for i, saved_target in enumerate(db.__root__):
    #             if saved_target == data:
    #                 db.__root__[i] = data
    #                 break
    #         else:
    #             db.__root__.append(data)
    #     db.save_to_file()

    @classmethod
    def add(cls, *data_array: Target) -> T.List[str]:
        db: Database = cls.load()
        for data in data_array:
            for saved_target in db.__root__:
                if saved_target == data:
                    saved_target.groups.update(data.groups)
                    break
            else:
                db.__root__.append(data)
        db.save_to_file()
        return [target.name for target in data_array]

    @classmethod
    def remove(cls, *data_array: Target) -> T.List[str]:
        db: Database = cls.load()
        for data in data_array:
            for saved_target in db.__root__:
                if saved_target == data:
                    # noinspection Mypy
                    [saved_target.groups.discard(group) for group in data.groups]
                    break
            else:
                pass
        db.save_to_file()
        return [target.name for target in data_array]

    @classmethod
    def show(cls, group_id: int) -> T.List[str]:
        db: Database = cls.load()
        ret = [saved_target.name for saved_target in db.__root__ if group_id in saved_target.groups]
        return ret
