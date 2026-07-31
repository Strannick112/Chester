import codecs
import io
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
        self.model = AchievementsModel(self.chester_bot)
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
            try:
                embed_picture = discord.File(main_config["achievement_embed_picture"])
            except OSError:
                return
            await self.channel.send(file=embed_picture)
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
        try:
            await self.message.edit(**(await self.view.update()))
            print("achievements updated")
        except:
            print("achievements NOT updated")
            pass

    @commands.command(name=main_config['short_server_name'] + "_get_achievements_info")
    @commands.has_role(main_config['master_role'])
    async def get_achievements_info(self, ctx, ku_id: str):
        """
            Отображает полную статистику игрока, сколько баллов и за что выдано для доски рейтинга:
            ku_id - уникальный klei_id игрока в игре
        """
        reader = self.model.reader
        stat = await reader.get_player_stat( reader.get_player_saves(key = lambda x: x == ku_id)[0][1] )
        text_message = f"""Подробная информация об игроке "{ku_id}": 
        ```json
        {stat} 
        ```"""
        if len(text_message) < 4000:
            await ctx.send(text_message)
        else:
            await ctx.send(file = discord.File(fp=io.BytesIO(text_message.encode('utf-8')), filename=f"{ku_id}.txt"))
