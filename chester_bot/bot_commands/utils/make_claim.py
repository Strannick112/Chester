import re

from chester_bot import main_config, wipes
from chester_bot.wipes.Claim import Claim
from chester_bot.wipes.Item import Item
from chester_bot.wipes.Player import Player


def make_claim(text: str, author: str, created_at: str):
    if message := re.findall(
            r'''Сервер:[\s]*?''' + main_config['server_name']
            + '''[\s]*?Игровой ник:[\s]*?([\w\d\s]+?)[\s]+?Прошу:[\s]*?([\w\W]+)''',
            text
    ):
        loot = re.findall(r'''(\w[\w\s].+?) \("([\w].+?)"\)''', message[0][1])
        print(f"Игровой ник: {message[0][0]}")
        for item in loot:
            print(f"Игровое название предмета: {item[0]}")
            print(f"Код для консоли: {item[1]}")
        return Claim(
            Player(author, message[0][0]),
            tuple(Item(item[0], item[1]) for item in loot),
            created_at,
            wipes.last_wipe.path,
        )
    return None
