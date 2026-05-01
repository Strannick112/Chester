import codecs
import json
import os

import discord
from discord.ext import tasks, commands

from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.AchievementsModel import AchievementsModel
from chesterbot.cogs.AchievementsDashBoard.AchievementsView import AchievementsView


class AchievementsController(commands.Cog, name="Доска статистики"):
    def __init__(self, bot):
        self.chester_bot = bot
        self.channel = None
        self.message = None
        self.message_id = None
        self.model = AchievementsModel()
        self.view = AchievementsView(self.model)

    async def on_ready(self):
        self.channel = self.chester_bot.get_channel(main_config["achievements_channel"])
        if not os.path.exists("./chesterbot/cogs/achievements"):
            os.mkdir("./chesterbot/cogs/achievements")
        if not os.path.exists(f"./chesterbot/cogs/achievements/message.json"):
            with codecs.open(f"./chesterbot/cogs/achievements/message.json", "w", encoding="utf-8") as file:
                json.dump(0, file)

        with codecs.open(f"./chesterbot/cogs/achievements/message.json", "rb", encoding="utf-8") as file:
            self.message_id = json.load(file)

        try:
            self.message = await self.channel.fetch_message(self.message_id)
        except:
            embed = discord.Embed(
                title="Статистика",
                description="Доска создана, начат сбор информации...",
                colour=discord.Colour.dark_teal()
            )
            self.message = await self.channel.send(embeds=[embed])
            self.message_id = self.message.id
            with codecs.open(f"./chesterbot/cogs/achievements/message.json", "w", encoding="utf-8") as file:
                json.dump(self.message_id, file)
        self.reload_data.start()

    @tasks.loop(minutes=1)
    async def reload_data(self):
        await self.model.update_data()
        try:
            await self.message.edit(**(await self.model.update_data()))
        except:
            pass
