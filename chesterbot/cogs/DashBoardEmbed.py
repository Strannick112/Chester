import asyncio
import codecs
import json
import os

import discord
from discord.ext import tasks, commands

from chesterbot import main_config
from chesterbot.cogs.ResourceDashBoard import ResourceDashBoard
from chesterbot.cogs.ScreenEmbed import ScreenEmbed
from chesterbot.cogs.ServerDashBoard import ServerDashBoard


class DashBoardEmbed(commands.Cog, name="Доска подсчёта"):
    def __init__(self, bot):
        self.chester_bot = bot
        self.world_dashboards = None
        self.screenEmbed = None

    async def __get_view(self):
        view = discord.ui.View()
        style = discord.ButtonStyle.gray
        for button_description in main_config["buttons"]:
            view.add_item(
                item=discord.ui.Button(
                    style=style, label=button_description["description"],
                    url=button_description["url"]
                )
            )
        return view

    async def __get_embed_list_default(self):
        embed_list_default = []
        for world in main_config["worlds"]:
            embed_list_default.append(
                discord.Embed(
                    title=world["public_name"],
                    description="Доска создана, начат сбор информации...",
                    colour=discord.Colour.dark_teal()
                )
            )
        return embed_list_default

    async def on_ready(self):
        embed_list_default = await self.__get_embed_list_default()
        try:
            embed_picture = discord.File(main_config["main_embed_picture"])
        except OSError:
            return
        self.world_dashboards = [ServerDashBoard(self.chester_bot, main_config["worlds"][0])]
        self.world_dashboards += [ResourceDashBoard(self.chester_bot, world) for world in main_config["worlds"]]
        view = await self.__get_view()
        self.screenEmbed = ScreenEmbed(
            name="dashboard",
            channel=self.chester_bot.get_channel(main_config["dashboard_channel"]),
            bot=self.chester_bot,
            embed_list_default=embed_list_default,
            view=view,
            update_callback=self.reload_data
        )
        await self.screenEmbed.on_ready()
        await self.screenEmbed.saved_picture_message.message.edit(attachments=[embed_picture])

    async def reload_data(self):
        await asyncio.wait([asyncio.create_task(world.reload_data()) for world in self.world_dashboards])
        return [await world.make_dashboard() for world in self.world_dashboards]


