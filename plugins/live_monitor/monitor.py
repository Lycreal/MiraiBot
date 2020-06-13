from pathlib import Path
from typing import List, Set, Tuple, Type, Optional

from config import data_path
from .._utils.register import Target, Database
from .channels import BaseChannel, LiveCheckResponse
from .enums import ChannelTypes


class Monitor:
    def __init__(self, channel: ChannelTypes):
        self.channel_type = channel.name
        self.channel: Type[BaseChannel] = channel.value

        Path(data_path).mkdir(exist_ok=True)
        self.save_file = Path(data_path).joinpath(f'{self.channel_type}.json')

        self.database: Database = Database.load(self.save_file)
        self.channels: List[BaseChannel] = [self.channel(target.t_id) for target in self.database.__root__]

        self.pos = -1

    def add(self, cid: str, group: int):
        self.database.add(Target(t_id=cid, platform=self.channel_type, groups={group}))
        self.database.save(self.save_file)
        for channel in self.channels:
            if channel.cid == cid:
                return False
        else:
            self.channels.append(self.channel(cid))
            return True

    def remove(self, cid: str, group: int):
        for channel in self.channels:
            if cid == channel.ch_name:
                cid = channel.cid
            if cid == channel.cid:
                self.database.remove(Target(t_id=cid, platform=self.channel_type, groups={group}))
                self.database.save(self.save_file)
                return True
        else:
            return False

    def next(self) -> Optional[BaseChannel]:
        if self.channels:
            self.pos = self.pos + 1 if self.pos < len(self.channels) - 1 else 0
            return self.channels[self.pos]
        else:
            return None

    async def run(self, strategy=3) -> Tuple[Optional[LiveCheckResponse], Set[int]]:
        channel: BaseChannel = self.next()

        if channel:
            for target in self.database.__root__:
                if target.t_id == channel.cid:
                    break
            else:
                return None, set()  # Should not happen

            if not target.groups:
                self.channels.remove(channel)
                self.database.__root__.remove(target)
                self.database.save(self.save_file)
                return None, set()

            resp = await channel.update(strategy=strategy)

            target.name = channel.ch_name
            self.database.save(self.save_file)

            return resp, target.groups
        else:
            return None, set()
