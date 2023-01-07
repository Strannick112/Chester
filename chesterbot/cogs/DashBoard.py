import codecs
import json
import os.path

from discord.ext import commands, tasks

from chesterbot import main_config


class DashBoard(commands.Cog, name="Доска подсчёта"):
    def __init__(self, bot):
        self.chester_bot = bot
        self.chester_bot.event(self.on_ready)

    async def on_ready(self):
        self.channel = self.chester_bot.get_channel(main_config["game_log_sync_channel"])
        if not os.path.exists("./chesterbot/cogs/dashboard.json"):
            with codecs.open("./chesterbot/cogs/dashboard.json", "w", encoding="utf-8") as file:
                json.dump(0, file)
        with codecs.open("./chesterbot/cogs/dashboard.json", "rb", encoding="utf-8") as file:
            self.message_id = json.load(file)
        try:
            self.message = await self.channel.fetch_message(self.message_id)
        finally:
            self.message = await self.channel.send(content="Доска создана, начат сбор информации...")
            self.message_id = self.message.id
            with codecs.open("./chesterbot/cogs/dashboard.json", "w", encoding="utf-8") as file:
                json.dump(self.message_id, file)

    @tasks.loop(minutes=1)
    async def reload_dashboard(self):
        await self.message.edit(content=self.make_dashboard())

    def make_dashboard(self):
        data = self.get_data()
        return \
            f"""
            Вольт-коз: {data[1]["lightninggoat"]};
            Взрослых бифало: {data[1]["beefalo"]};
            Иглу: {data[1]["walrus_camp"]};
            Живых МакБивней: {data[1]["walrus"]};
            Домов свина: {data[1]["pighouse"]};
            Хижин зайца: {data[2]["rabbithouse"]};
            Кустов каменных фруктов: {data[1]["rock_avocado_bush"]};
            
            Гломмер: {data[1]["glommer"]};
            Дружелюбная плодовая муха: {data[1]["friendlyfruitfly"]};
            
            Мешок клауса: {data[1]["klaus_sack"]};
            Драконья муха: {data[1]["dragonfly"]};
            Улей пчелиной матки: {data[1]["beequeenhivegrown"]};
            
            Медведь-барсук: {data[1]["bearger"]};
            Гусь-лусей: {data[1]["moose"]};
            Яиц гусь-луся: {data[1]["mooseegg"]};
            Лусят: {data[1]["mossling"]};
            Муравьиный лев: {data[1]["antlion"]};
            Король крабов: {data[1]["crabking"]};
            
            Жаба-поганка: {data[2]["toadstool_cap"]};
            Древний страж: {data[2]["minotaur"]};
            
            Скелетов игроков: {data[1]["skeleton"]};
"""

    def get_data(self):
        return {}
