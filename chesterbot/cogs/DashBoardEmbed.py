import asyncio
import codecs
import json
import os

import discord
from discord.ext import tasks, commands

from chesterbot import main_config
from chesterbot.cogs.ResourceDashBoard import ResourceDashBoard
from chesterbot.cogs.ServerDashBoard import ServerDashBoard


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
                json.dump(0, file)

        with codecs.open(f"./chesterbot/cogs/dashboard/message.json", "rb", encoding="utf-8") as file:
            self.message_id = json.load(file)
        embed_list = [
            # discord.Embed(
            #     title=main_config["server_name"],
            #     description="Доска создана, начат сбор информации...",
            #     colour=discord.Colour.dark_teal()
            # )
        ]
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
            self.message = await self.channel.send(embeds=embed_list, file=discord.File(main_config["main_embed_picture"]))
            self.message_id = self.message.id
            with codecs.open(f"./chesterbot/cogs/dashboard/message.json", "w", encoding="utf-8") as file:
                json.dump(self.message_id, file)
        self.world_dashboards = [ServerDashBoard(self.chester_bot, main_config["worlds"][0])]
        self.world_dashboards += [ResourceDashBoard(self.chester_bot, world) for world in main_config["worlds"]]
        self.reload_data.start()

    async def update_dashboard(self):
        # head_embed = discord.Embed(color=0x2F3136)
        # head_embed.set_image(url=main_config["main_embed_picture"])
        # dashboard = [head_embed]
        dashboard = [await world.make_dashboard() for world in self.world_dashboards]
        # for i in range(1, dashboard.__len__()):
        #     dashboard[i].set_image(url="https://media.discordapp.net/attachments/871824345780080690/1152211515106136104/image.png")
        view = discord.ui.View()
        style = discord.ButtonStyle.gray
        view.add_item(
            item=discord.ui.Button(
                style=discord.ButtonStyle.primary, label="Узнай больше о сервере",
                url="https://discord.com/channels/794687419105411082/968907992575668275/970776984068161556"
            )
        )
        for button_description in main_config["buttons"]:
            view.add_item(
                item=discord.ui.Button(
                    style=style, label=button_description["description"],
                    url=button_description["url"]
                )
            )
        try:
            await self.message.edit(embeds=dashboard, view=view)
        finally:
            pass

    @tasks.loop(minutes=1)
    async def reload_data(self):
        tasks = [asyncio.create_task(world.reload_data()) for world in self.world_dashboards]
        for task in tasks:
            await task
        await self.update_dashboard()
