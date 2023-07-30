import asyncio
import codecs
import json
import os
import re
import shlex
import subprocess

from chesterbot.ConsoleDSTChecker import ConsoleDSTChecker
from chesterbot.config import main_config
from chesterbot.wipes import main_dir
from chesterbot.wipes.Item import Item
from chesterbot.wipes.Player import Player
from chesterbot.wipes.Status import Status


class Claim:
    def __init__(
            self,
            player: Player = None,
            items: tuple[Item] = tuple(),
            created_at: str = "",
            path: str = "",
            approved_at: str = "",
            executed_at: str = "",
            status: str = Status.not_approved
    ):
        self.player = player
        self.items = items
        self.status = status
        self.created_at = created_at
        self.approved_at = approved_at
        self.executed_at = executed_at
        self.path = path

    def save(self):
        """Сохраняет данные объекта в файл"""
        with codecs.open(
                f"{main_dir}/{self.path}/claims/{self.player.discord_nickname}.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(self, file, default=lambda o: o.__dict__, indent=4, ensure_ascii=False)

    def delete(self):
        tmp_path = f"{main_dir}/{self.path}/claims/{self.player.discord_nickname}.json"
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

    @staticmethod
    def from_dict(raw_dict):
        return Claim(
            Player.from_dict(raw_dict['player']),
            tuple(Item.from_dict(args) for args in raw_dict['items']),
            raw_dict['created_at'],
            raw_dict['path'],
            raw_dict['approved_at'],
            raw_dict['executed_at'],
            raw_dict['status'],
        )

    async def give_items(self, executed_at: str, console_dst_checker: ConsoleDSTChecker) -> bool:
        if self.status == Status.approved:
            print("approved!")
            for world in main_config["worlds"]:
                print("shard:", world["shard_id"])
                for item in self.items:
                    dst_nickname = re.sub(r'\'', r"\\\\\'", self.player.dst_nickname)
                    dst_nickname = re.sub(r'\"', r"\\\\\"", dst_nickname)
                    item_id = shlex.quote(item.id)
                    command = f"""screen -S {world["screen_name"]} -X stuff"""\
                        f""" "UserToPlayer(\\\"{dst_nickname}\\\").components.inventory:"""\
                        f"""GiveItem(SpawnPrefab(\\\"{item_id}\\\"))\n\""""
                    result = await console_dst_checker.check(
                        command,
                        r'\[string "UserToPlayer\("(' +
                        dst_nickname +
                        r')"\)[\w\W]*?\.\.\."\]\:1\: attempt to index a nil value',
                        world["shard_id"], world["screen_name"], "is_normal", 5
                        )
                    print("result:", result)
                    if result == dst_nickname:
                        break
                else:
                    self.executed_at = executed_at
                    self.status = Status.executed
                    self.save()
                    return True
        return False

    def rollback_claim(self) -> bool:
        if self.status == Status.executed:
            self.executed_at = ""
            self.status = Status.approved
            self.save()
            return True
        else:
            return False

    def equal(self, claim):
        if self.player.discord_nickname == claim.player.discord_nickname:
            return True
        else:
            return False

    def approve(self, approved_at: str) -> bool:
        if self.status == Status.not_approved:
            self.approved_at = approved_at
            self.status = Status.approved
            self.save()
            return True
        else:
            return False