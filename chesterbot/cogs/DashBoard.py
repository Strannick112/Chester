import asyncio
import codecs
import json
import os.path
import re

from discord.ext import commands, tasks

from chesterbot import main_config


class DashBoard(commands.Cog, name="Доска подсчёта"):
    def __init__(self, bot, world):
        self.chester_bot = bot
        self.shard_id = world["shard_id"]
        self.public_name = world["public_name"]
        self.screen_name = main_config['short_server_name'] + self.shard_id.__str__()
        self.data = DashBoard.__data[world["world_type"]].copy()
        self.__cog_name__ += self.screen_name

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
        self.chat_channel = self.chester_bot.get_channel(main_config["game_chat_sync_channel"])
        self.log_channel = self.chester_bot.get_channel(main_config["game_log_sync_channel"])
        if not os.path.exists("./chesterbot/cogs/dashboard"):
            os.mkdir("./chesterbot/cogs/dashboard")
        if not os.path.exists(f"./chesterbot/cogs/dashboard/{self.shard_id}.json"):
            with codecs.open(f"./chesterbot/cogs/dashboard/{self.shard_id}.json", "w", encoding="utf-8") as file:
                json.dump((0, 0), file)

        with codecs.open(f"./chesterbot/cogs/dashboard/{self.shard_id}.json", "rb", encoding="utf-8") as file:
            self.chat_message_id, self.log_message_id = json.load(file)

        try:
            self.chat_message = await self.chat_channel.fetch_message(self.chat_message_id)
        except:
            self.chat_message = await self.chat_channel.send(content="Доска создана, начат сбор информации...")
            self.chat_message_id = self.chat_message.id
            with codecs.open(f"./chesterbot/cogs/dashboard/{self.shard_id}.json", "w", encoding="utf-8") as file:
                json.dump((self.chat_message_id, self.log_message_id), file)

        try:
            self.log_message = await self.log_channel.fetch_message(self.log_message_id)
        except:
            self.log_message = await self.log_channel.send(content="Доска создана, начат сбор информации...")
            self.log_message_id = self.log_message.id
            with codecs.open(f"./chesterbot/cogs/dashboard/{self.shard_id}.json", "w", encoding="utf-8") as file:
                json.dump((self.chat_message_id, self.log_message_id), file)

        self.reload_data.start()

    async def update_dashboard(self):
        dashboard = self.make_dashboard()
        await self.log_message.edit(content=dashboard)
        await self.chat_message.edit(content=dashboard)


    def make_dashboard(self):
        text = "```"
        text += self.public_name + "\n\n"
        for group_name, group in self.data.items():
            text += group_name + ":\n\n"
            for prefab_name, prefab_info in group.items():
                text += prefab_name + ": " + (sum(prefab_info.values()).__str__()) + ";\n"
            text += "\n"
        text += "```"
        return text

    @tasks.loop(minutes=1)
    async def reload_data(self):
        for group_name, group in self.data.items():
            for prefab_name, prefab_info in group.items():
                for prefab_code, prefab_count in prefab_info.items():
                    true_command = f"""c_countprefabs("{prefab_code}")"""
                    packed_command = re.sub(r'\"', r"\"", re.sub(r'\'', r"\'", true_command))
                    linux_command = f"""screen -S {self.screen_name} -X stuff "{packed_command}\n\""""
                    # print("")
                    prefab_count = await asyncio.create_task(
                        self.chester_bot.console_dst_checker.check(
                            linux_command, r"There are\s+([\d])+\s+" + prefab_code + "[\w\W]+", self.shard_id, self.screen_name
                        )
                    )
                    print(prefab_code, ": ", prefab_count)
            await asyncio.sleep(5)
            await self.update_dashboard()
