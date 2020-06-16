import typing as T
import json
from pathlib import Path
from pydantic import BaseModel, ValidationError

from config import data_path

Path(data_path).mkdir(exist_ok=True)


class Target(BaseModel):
    name: str = ''
    id: str
    groups: T.Set[int]

    def __str__(self):
        return self.name or self.id


class Database(BaseModel):
    __root__: T.List[Target] = []

    @classmethod
    def load(cls, file: Path) -> "Database":
        try:
            db: Database = cls.parse_file(file)
        except (FileNotFoundError, json.JSONDecodeError, ValidationError):
            db = cls()
        return db

    def save(self, file: Path) -> None:
        with file.open('w', encoding='utf8') as f:
            json.dump([json.loads(target.json()) for target in self.__root__], f, ensure_ascii=False, indent=2)

    def add(self, target: Target) -> None:
        for saved_target in self.__root__:
            if saved_target.id == target.id:
                saved_target.groups.update(target.groups)
                break
        else:
            self.__root__.append(target)

    def remove(self, target: Target) -> bool:
        for saved_target in self.__root__:
            if saved_target.id == target.id:
                # noinspection Mypy
                [saved_target.groups.discard(group) for group in target.groups]
                return True
        else:
            return False

    def show(self, group_id: int) -> T.List[Target]:
        ret = [saved_target for saved_target in self.__root__ if group_id in saved_target.groups]
        return ret
