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
    def __init__(self, bot):
        self.chester_bot = bot
        self.data = {
            1: {
                "lightninggoat": 0,
                "beefalo": 0,
                "walrus_camp": 0,
                "walrus": 0,
                "pighouse": 0,
                "rock_avocado_bush": 0,
                "glommer": 0,
                "friendlyfruitfly": 0,
                "klaus_sack": 0,
                "dragonfly": 0,
                "beequeenhivegrown": 0,
                "bearger": 0,
                "mooseegg": 0,
                "moose": 0,
                "mossling": 0,
                "antlion": 0,
                "crabking": 0,
                "skeleton": 0,
            }
        }
        self.file_first_iterator = subprocess.Popen(
            ['tail', '-F', '-n1', main_config["path_to_log"]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        self.file_first_poll = select.poll()
        self.file_first_poll.register(self.file_first_iterator.stdout)

    async def on_ready(self):
        self.chat_channel = self.chester_bot.get_channel(main_config["game_chat_sync_channel"])
        self.log_channel = self.chester_bot.get_channel(main_config["game_log_sync_channel"])

        if not os.path.exists("./chesterbot/cogs/dashboard.json"):
            with codecs.open("./chesterbot/cogs/dashboard.json", "w", encoding="utf-8") as file:
                json.dump((0, 0), file)

        with codecs.open("./chesterbot/cogs/dashboard.json", "rb", encoding="utf-8") as file:
            self.chat_message_id, self.log_message_id = json.load(file)

        try:
            self.chat_message = await self.chat_channel.fetch_message(self.chat_message_id)
        except:
            self.chat_message = await self.chat_channel.send(content="Доска создана, начат сбор информации...")
            self.chat_message_id = self.chat_message.id
            with codecs.open("./chesterbot/cogs/dashboard.json", "w", encoding="utf-8") as file:
                json.dump((self.chat_message_id, self.log_message_id), file)

        try:
            self.log_message = await self.log_channel.fetch_message(self.log_message_id)
        except:
            self.log_message = await self.log_channel.send(content="Доска создана, начат сбор информации...")
            self.log_message_id = self.log_message.id
            with codecs.open("./chesterbot/cogs/dashboard.json", "w", encoding="utf-8") as file:
                json.dump((self.chat_message_id, self.log_message_id), file)

        self.reload_data.start()
        self.on_server_log.start()

    async def update_dashboard(self):
        dashboard = self.make_dashboard()
        await self.log_message.edit(content=dashboard)
        await self.chat_message.edit(content=dashboard)

    def make_dashboard(self):
        return \
            f"""```
Вольт-коз: {self.data[1]["lightninggoat"]};
Взрослых бифало: {self.data[1]["beefalo"]};
Иглу: {self.data[1]["walrus_camp"]};
Живых МакБивней: {self.data[1]["walrus"]};
Домов свина: {self.data[1]["pighouse"]};
Кустов каменных фруктов: {self.data[1]["rock_avocado_bush"]};

Гломмер: {self.data[1]["glommer"]};
Дружелюбная плодовая муха: {self.data[1]["friendlyfruitfly"]};

Мешок клауса: {self.data[1]["klaus_sack"]};
Драконья муха: {self.data[1]["dragonfly"]};
Улей пчелиной матки: {self.data[1]["beequeenhivegrown"]};

Медведь-барсук: {self.data[1]["bearger"]};
Гусь-лусей: {self.data[1]["moose"]};
Яиц гусь-луся: {self.data[1]["mooseegg"]};
Лусят: {self.data[1]["mossling"]};
Муравьиный лев: {self.data[1]["antlion"]};
Король крабов: {self.data[1]["crabking"]};

Скелетов игроков: {self.data[1]["skeleton"]};```
"""

    @tasks.loop(minutes=1)
    async def reload_data(self):
        screen_list = subprocess.run(
            'screen -ls',
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        ).stdout.decode('ascii')
        if main_config['server_main_screen_name'] in screen_list:
            for prefab in self.data[1]:
                true_command = f"""c_countprefabs("{prefab}")"""
                packed_command = re.sub(r'\"', r"\"", re.sub(r'\'', r"\'", true_command))
                linux_command = f"""screen -S {main_config['server_main_screen_name']} -X stuff "{packed_command}\n\""""
                subprocess.check_output(linux_command, shell=True)
            await asyncio.sleep(5)
            await self.update_dashboard()

    @tasks.loop(seconds=0.1)
    async def on_server_log(self):
        """Следить за логами на игровом сервере"""
        if self.file_first_poll.poll(1):
            try:
                text = self.file_first_iterator.stdout.readline()[12:]
                if "There are" in text:
                    for prefab in self.data[1].keys():
                        if prefab in text:
                            self.data[1][prefab] = re.findall(r"([\d]+)", text)[0]
                            break
            except Exception as error:
                print(error)

