import codecs
import json
import os
import re
import shlex
import subprocess

from chester_bot.config import main_config
from chester_bot.wipes import main_dir
from chester_bot.wipes.Item import Item
from chester_bot.wipes.Player import Player
from chester_bot.wipes.Status import Status


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

    def give_items(self, executed_at: str) -> bool:
        if self.status == Status.approved:
            for item in self.items:
                dst_nickname = re.sub(r'\'', r"\\\\\'", self.player.dst_nickname)
                dst_nickname = re.sub(r'\"', r"\\\\\"", dst_nickname)
                # dst_nickname = shlex.quote(self.player.dst_nickname)
                item_id = shlex.quote(item.id)
                print(
                    subprocess.check_output(
                        f"""screen -S {main_config['server_main_screen_name']} -X stuff "UserToPlayer(\\\"{dst_nickname}\\\").components.inventory:GiveItem(SpawnPrefab(\\\"{item_id}\\\"))\n\"""",
                        shell=True
                    )
                )
                # os.system(
                #     f'''screen -S {main_config['server_main_screen_name']} -X stuff "UserToPlayer(\"{self.player.dst_nickname}\").components.inventory:GiveItem(SpawnPrefab(\"{item.id}\"))\n\"'''
                # )
            self.executed_at = executed_at
            self.status = Status.executed
            self.save()
            return True
        else:
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