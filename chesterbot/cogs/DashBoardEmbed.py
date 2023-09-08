import codecs
import json
import os

import discord
from discord.ext import tasks, commands

from chesterbot import main_config
from chesterbot.cogs.DashBoard import DashBoard


class DashBoardEmbed(commands.Cog, name="Доска подсчёта"):
    def __init__(self, bot):
        self.chester_bot = bot
        self.channel = None
        self.message = None
        self.message_id = None
        self.world_dashboards = None

    async def on_ready(self):
        self.channel = self.chester_bot.get_channel(main_config["dashboard_channel"])
        if not os.path.exists("./chesterbot/cogs/dashboard"):
            os.mkdir("./chesterbot/cogs/dashboard")
        if not os.path.exists(f"./chesterbot/cogs/dashboard/message.json"):
            with codecs.open(f"./chesterbot/cogs/dashboard/message.json", "w", encoding="utf-8") as file:
                json.dump((0, 0), file)

        with codecs.open(f"./chesterbot/cogs/dashboard/message.json", "rb", encoding="utf-8") as file:
            self.message_id = json.load(file)
        embed_list = []
        for world in main_config["worlds"]:
            embed_list.append(
                discord.Embed(
                    title=world["public_name"],
                    description="Доска создана, начат сбор информации...",
                    colour=discord.Colour.dark_teal()
                )
            )
        try:
            self.message = await self.channel.fetch_message(self.message_id)
        except:
            self.message = await self.channel.send(embed=embed_list)
            self.message_id = self.message.id
            with codecs.open(f"./chesterbot/cogs/dashboard/message.json", "w", encoding="utf-8") as file:
                json.dump(self.message_id, file)
        self.world_dashboards = [DashBoard(self.chester_bot, world) for world in main_config["worlds"]]
        self.reload_data.start()

    async def update_dashboard(self):
        dashboard = [await world.make_dashboard() for world in self.world_dashboards]
        try:
            await self.message.edit(embed=dashboard)
        finally:
            pass

    @tasks.loop(minutes=1)
    async def reload_data(self):
        for world in self.world_dashboards:
            await world.reload_data()
        await self.update_dashboard()
