import asyncio
import codecs
import json
import os.path
import re
import select
import subprocess

from discord.ext import commands, tasks

from chesterbot import main_config


class DashBoard(commands.Cog, name="Доска подсчёта"):
    def __init__(self, bot, public_name, shard_id, world_type, folder_name):
        self.chester_bot = bot
        self.shard_id = shard_id
        self.public_name = public_name
        self.path_to_log = main_config['path_to_save'] + "/" + folder_name + "/server_log.txt"
        self.screen_name = main_config['short_server_name'] + self.shard_id.__str__()
        self.data = DashBoard.data[world_type].copy()
        self.file_first_iterator = subprocess.Popen(
            ['tail', '-F', '-n1', self.path_to_log],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )
        self.file_first_poll = select.poll()
        self.file_first_poll.register(self.file_first_iterator.stdout)

    data = {
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
                "Хижины моржей:": {"walrus_camp": 0},
                "Моржи": {"walrus": 0},
                "Дома свиней": {"pighouse": 0},
            },
            "Ресурсы": {
                "Кусты камыша": {"reeds": 0},
                "Кусты каменных фруктов": {"rock_avocado_bush": 0},
            }

        },
        "caves": {
            "Боссы": {
                "Гриб Жабы-поганки": {"toadstool_cap": 0},
                "Древний страж": {"minotaur": 0},
                "Дружелюбная фруктовая муха": {"friendlyfruitfly": 0},
                "Скелеты игроков": {"skeleton": 0},
            },
            "Монстры": {
                "Проглоты": {"slurper": 0},
                "Глубинные черви": {"worm": 0},
                "Лобстеры": {"rocky": 0},
                "Дома зайцев": {"rabbithouse": 0},
            },
            "Ресурсы": {
                "Статуи в руинах с самоцветами": {"ruins_statue_mage": 0},
                "Статуи в руинах без самоцветов": {"ruins_statue_mage_nogem": 0},
                "Головы в руинах с самоцветами": {"ruins_statue_head": 0},
                "Головы в руинах без самоцветов": {"ruins_statue_head_nogem": 0},
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
        self.on_server_log.start()

    async def update_dashboard(self):
        dashboard = self.make_dashboard()
        await self.log_message.edit(content=dashboard)
        await self.chat_message.edit(content=dashboard)


    def make_dashboard(self):
        text = "```"
        text += self.public_name + "\n\n"
        for group_name, group in self.data.items():
            text += group_name + ":\n\n"
            for name, prefab in group:
                text += name + ": " + (prefab.values())[0].__str__() + ";\n"
            text += "\n"
        text += "```"
        return text

    @tasks.loop(minutes=1)
    async def reload_data(self):
        screen_list = subprocess.run(
            'screen -ls',
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        ).stdout.decode('ascii')
        if self.screen_name in screen_list:
            for group_name, group in self.data.items():
                for prefab_name, prefab_info in group.items():
                    for prefab_code, prefab_count in prefab_info.items():
                        true_command = f"""c_countprefabs("{prefab_code}")"""
                        packed_command = re.sub(r'\"', r"\"", re.sub(r'\'', r"\'", true_command))
                        linux_command = f"""screen -S {self.screen_name} -X stuff "{packed_command}\n\""""
                        try:
                            subprocess.check_output(linux_command, shell=True)
                        except Exception as error:
                            print(error)
            await asyncio.sleep(5)
            await self.update_dashboard()

    @tasks.loop(seconds=0.1)
    async def on_server_log(self):
        """Следить за логами на игровом сервере"""
        if self.file_first_poll.poll(1):
            try:
                text = self.file_first_iterator.stdout.readline()[12:]
                if "There are" in text:
                    for group_name, group in self.data.items():
                        for prefab_name, prefab_info in group.items():
                            for prefab_code, prefab_count in prefab_info.items():
                                if prefab_code in text:
                                    self.data[group_name][prefab_name][prefab_code] = re.findall(r"([\d]+)", text)[0]
                                    break
            except Exception as error:
                print(error)

