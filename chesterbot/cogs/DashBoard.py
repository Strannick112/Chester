import asyncio
import codecs
import json
import os.path
import re
import select
import subprocess
import time

from discord.ext import commands, tasks

from chesterbot import main_config


class DashBoard(commands.Cog, name="Доска подсчёта"):
    def __init__(self, bot):
        self.chester_bot = bot
        self.chester_bot.event(self.on_ready)
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
            ['tail', '-F', main_config["path_to_log"]],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # encoding="utf-8",
            # text=True
        )
        self.file_first_poll = select.poll()
        self.file_first_poll.register(self.file_first_iterator.stdout)

    async def on_ready(self):
        self.channel = self.chester_bot.get_channel(main_config["game_log_sync_channel"])
        if not os.path.exists("./chesterbot/cogs/dashboard.json"):
            with codecs.open("./chesterbot/cogs/dashboard.json", "w", encoding="utf-8") as file:
                json.dump(0, file)
        with codecs.open("./chesterbot/cogs/dashboard.json", "rb", encoding="utf-8") as file:
            self.message_id = json.load(file)
        try:
            self.message = await self.channel.fetch_message(self.message_id)
        except:
            self.message = await self.channel.send(content="Доска создана, начат сбор информации...")
            self.message_id = self.message.id
            with codecs.open("./chesterbot/cogs/dashboard.json", "w", encoding="utf-8") as file:
                json.dump(self.message_id, file)
        self.reload_data.start()
        self.on_server_log.start()

    async def update_dashboard(self):
        await self.message.edit(content=self.make_dashboard())

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
        for shard_id in self.data:
            for prefab in self.data[shard_id]:
                true_command = f"""c_countprefabs("{prefab}")"""
                packed_command = re.sub(r'\"', r"\"", re.sub(r'\'', r"\'", true_command))
                linux_command = f"""screen -S {main_config['short_server_name']}{shard_id} -X stuff "{packed_command}\n\""""
                subprocess.check_output(linux_command, shell=True)
        await asyncio.sleep(5)
        await self.update_dashboard()

    @tasks.loop(seconds=0.1)
    async def on_server_log(self):
        """Следить за логами на игровом сервере"""
        if self.file_first_poll.poll(1):
            try:
                text = self.file_first_iterator.stdout.readline().decode(encoding="utf-8")[12:]
                if "There are" in text:
                    print(text)
                    for prefab in self.data[1].keys():
                        if prefab in text:
                            print(re.findall(r"([%d]+?)", text)[0])
                            self.data[1][prefab] = re.findall(r"\t(%d.?)\t", text)[0]
                            break
            except Exception as error:
                print(error)

