import asyncio

import discord
from discord.ext import commands

from chesterbot import main_config
from chesterbot.screens.dashboard.ResourceInfo import ResourceInfo
from chesterbot.screens.dashboard.DashboardView import DashboardView
from chesterbot.screens.dashboard.ServerInfo import ServerDashboard


class DashboardEntity(commands.Cog, name="Доска подсчёта"):
    def __init__(self, bot):
        self.chester_bot = bot
        self.world_dashboards = None
        self.screenEmbed = None
        self.view = None

    @staticmethod
    async def __get_view():
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

    @staticmethod
    async def __get_embed_list_default():
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
        try:
            embed_picture = discord.File(main_config["main_embed_picture"])
        except OSError:
            return
        self.world_dashboards = [ServerDashboard(self.chester_bot, main_config["worlds"][0])]
        self.world_dashboards += [ResourceInfo(self.chester_bot, world) for world in main_config["worlds"]]
        self.view = await self.__get_view()
        self.screenEmbed = DashboardView(
            name="dashboard",
            channel=self.chester_bot.get_channel(main_config["dashboard_channel"]),
            bot=self.chester_bot,
            head_picture=embed_picture,
            embed_list_default=await self.__get_embed_list_default(),
            view=self.view,
            update_callback=self.update_stream_message
        )
        await self.screenEmbed.on_ready()

    async def update_stream_message(self):
        await asyncio.wait([asyncio.create_task(world.reload_data()) for world in self.world_dashboards])
        return {
            "embeds": [await world.make_dashboard() for world in self.world_dashboards],
            "view": self.view
        }
