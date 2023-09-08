import asyncio
import codecs
import json
import os.path
import random
import re

import discord
from discord.ext import commands, tasks

from chesterbot import main_config


class DashBoard(commands.Cog, name="Доска подсчёта"):
    def __init__(self, bot, world):
        self.chester_bot = bot
        self.shard_id = world["shard_id"]
        self.public_name = world["public_name"]
        self.screen_name = world["screen_name"]
        self.data = DashBoard.__data[world["world_type"]].copy()
        self.__cog_name__ += self.screen_name
        self.channel = None
        self.message = None
        self.message_id = None

    __data = {
        "overworld": {
            "Боссы": {
                "Дружелюбная фруктовая муха": {"friendlyfruitfly": 0},
                "Драконья муха": {"dragonfly": 0},
                "Гломмер": {"glommer": 0},
                "Мешок клауса": {"klaus_sack": 0},
                "Улей пчелиной королевы": {"beequeenhivegrown": 0},
                "Медведь-барсук": {"bearger": 0},
                "Яйца Гусь-лусей": {"mooseegg": 0},
                "Гусь-лусь": {"moose": 0},
                "Лусята": {"mossling": 0},
                "Муравьиный лев": {"antlion": 0},
                "Король-краб": {"crabking": 0},
                "Скелеты игроков": {"skeleton": 0},
        },
            "Монстры":{
                "Вольт-козы": {"lightninggoat": 0},
                "Бифало": {"beefalo": 0},
                "Хижины моржей": {"walrus_camp": 0},
                "Моржи": {"walrus": 0},
                "Дома свиней": {"pighouse": 0},
                "Дома мермов": {"mermhouse": 0},
                "Мермы": {"merm": 0},
                "Щупальца": {"tentacle": 0},
                "Шахматы": {"knight": 0, "bishop": 0, "rook": 0},
                "Енотокоты": {"catcoon": 0},
                "Дикие улья": {"beehive": 0},
                "Улья пчёл-убийц": {"wasphive": 0},
                "Смертоносные светлоцветы": {"lunarthrall_plant": 0},
            },
            "Ресурсы": {
                "Кусты камыша": {"reeds": 0},
                "Кусты каменных фруктов": {"rock_avocado_bush": 0},
                "Перекати-поле": {"tumbleweed": 0},
                "Спаунеры перекати-поле": {"tumbleweedspawner": 0},
                "Приманкоцветы": {"lureplant": 0},
                "Разломы": {"lunarrift_portal": 0},
                "Кристаллы разлома": {"lunarrift_crystal_big": 0},
            }
        },
        "caves": {
            "Боссы": {
                "Древний страж": {"minotaur": 0},
                "Дружелюбная фруктовая муха": {"friendlyfruitfly": 0},
                "Скелеты игроков": {"skeleton": 0},
            },
            "Монстры": {
                "Проглоты": {"slurper": 0},
                "Глубинные черви": {"worm": 0},
                "Лобстеры": {"rocky": 0},
                "Дома зайцев": {"rabbithouse": 0},
                "Логова мотыльков": {"dustmothden": 0},
                "Обезьяньи тотемы": {"monkeybarrel": 0},
                "Щупальца": {"tentacle": 0},
                "Повреждённых шахмат на охране руин": {
                    "knight_nightmare": 0,
                    "bishop_nightmare": 0,
                    "rook_nightmare": 0,
                },
                "Спилагмиты": {"spiderhole": 0},
            },
            "Ресурсы": {
                "Статуи в руинах": {
                    "ruins_statue_mage": 0,
                    "ruins_statue_mage_nogem": 0,
                    "ruins_statue_head": 0,
                    "ruins_statue_head_nogem": 0,
                },
                "Кусты камыша": {"reeds": 0},
                "Сундуки в лабиринте": {"pandoraschest": 0},
            }
        }
    }

    async def on_ready(self):
        self.channel = self.chester_bot.get_channel(main_config["dashboard_channel"])
        if not os.path.exists("./chesterbot/cogs/dashboard"):
            os.mkdir("./chesterbot/cogs/dashboard")
        if not os.path.exists(f"./chesterbot/cogs/dashboard/{self.shard_id}.json"):
            with codecs.open(f"./chesterbot/cogs/dashboard/{self.shard_id}.json", "w", encoding="utf-8") as file:
                json.dump((0, 0), file)

        with codecs.open(f"./chesterbot/cogs/dashboard/{self.shard_id}.json", "rb", encoding="utf-8") as file:
            self.message_id = json.load(file)

        embed = discord.Embed(
            title=self.public_name,
            description="Доска создана, начат сбор информации...",
            colour=discord.Colour.dark_teal()
        )
        try:
            self.message = await self.channel.fetch_message(self.message_id)
        except:
            self.message = await self.channel.send(embed=embed)
            self.message_id = self.message.id
            with codecs.open(f"./chesterbot/cogs/dashboard/{self.shard_id}.json", "w", encoding="utf-8") as file:
                json.dump(self.message_id, file)

        self.reload_data.start()

    async def update_dashboard(self):
        dashboard = self.make_dashboard()
        try:
            await self.message.edit(embed=dashboard)
        finally:
            pass

    def make_dashboard(self):
        embed = discord.Embed(title="Доска подсчёта", colour=discord.Colour.dark_teal())
        embed.set_author(name=self.public_name, url=self.chester_bot.replies["announcement_picture"])
        for group_name, group in self.data.items():
            text = ""
            for prefab_name, prefab_info in group.items():
                text += prefab_name + ": " + (sum(prefab_info.values()).__str__()) + ";\n"
            embed.add_field(name=group_name, value=text, inline=True)
        return embed

    @tasks.loop(minutes=1)
    async def reload_data(self):
        for group_name, group in self.data.items():
            for prefab_name, prefab_info in group.items():
                for prefab_code, prefab_count in prefab_info.items():
                    command = f"screen -S {self.screen_name} -X stuff "\
                                     f"\"local count = 0 local prefab = \\\"{prefab_code}\\\" "\
                                     "for k,v in pairs(Ents) do if v.prefab == prefab then "\
                                     "count = count + 1 end end print(\\\"CountPrefab\\\", prefab, count)\n\""
                    self.data[group_name][prefab_name][prefab_code] = int(
                        await asyncio.create_task(
                            self.chester_bot.console_dst_checker.check(
                                command, r"CountPrefab\s*" + prefab_code + r"\s*([\d]+)\s*",
                                self.shard_id, self.screen_name, prefab_count, 30
                            )
                        )
                    )
            await asyncio.sleep(random.randint(3, 10))
            await self.update_dashboard()
