import codecs
import json

import discord
from aiohttp import BasicAuth
from discord.ext import commands

from chesterbot import main_config
from chesterbot.ConsoleDSTChecker import ConsoleDSTChecker
from chesterbot.cogs import BotManage, WipeManage
from chesterbot.cogs.Halloween import Halloween
from chesterbot.cogs.DashBoardEmbed import DashBoardEmbed
from chesterbot.cogs.server_manage import ServerManage
from chesterbot.cogs.server_manage.commands import send_message_to_game
from chesterbot.cogs.wipe_manage.models import models_init


class ChesterBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True
        self.default_role = None
        self.console_dst_checker = ConsoleDSTChecker(main_config["worlds"])

        with codecs.open("./chesterbot/replies.json", "r", encoding="utf-8") as file:
            self.replies = json.load(file)
            self.replies["claim_channel_id"] = json.loads(self.replies["claim_channel_id"])
            self.replies["commands_channel_id"] = json.loads(self.replies["commands_channel_id"])
        self.server_manage = ServerManage(self)
        self.bot_manage = BotManage(self)
        self.wipe_manage = WipeManage(self)
        self.dashboards = DashBoardEmbed(self)
        self.halloween = Halloween(self)
        self.event(self.on_ready)
        if main_config["proxy"]["address"] == "":
            super().__init__(
                command_prefix=main_config['prefix'],
                intents=intents
            )
        else:
            super().__init__(
                command_prefix=main_config['prefix'],
                intents=intents,
                proxy=main_config["proxy"]["address"]
            )

        self.async_session = None

    async def on_ready(self):
        self.async_session = await models_init()
        await self.user.edit(username="Chester")
        await self.server_manage.on_ready()
        await self.console_dst_checker.on_ready(self.loop)
        await self.wipe_manage.on_ready()
        await self.dashboards.on_ready()


    async def init(self):
        # pass
        await self.add_cog(self.server_manage)
        await self.add_cog(self.bot_manage)
        await self.add_cog(self.wipe_manage)
        await self.add_cog(self.dashboards)
        await self.add_cog(self.halloween)

    async def start(self, token: str = main_config['token'], *, reconnect: bool = True):
        await self.init()
        await super().start(token)

    def run(self, token: str = main_config['token'], *args, **kwargs):
        super().run(token=token, *args, **kwargs)

    def reload_replies(self):
        with codecs.open("./chesterbot/replies.json", "r", encoding="utf-8") as file:
            self.replies = json.load(file)
            self.replies["claim_channel_id"] = json.loads(self.replies["claim_channel_id"])
            self.replies["commands_channel_id"] = json.loads(self.replies["commands_channel_id"])

    async def on_message(self, message):
        if not message.author.bot:
            if len(message.content) > 0:
                # When command
                if message.content[0] == main_config['prefix']:
                    if message.channel.id in self.replies['commands_channel_id']:
                        await self.process_commands(message)
                # When a message
                else:
                    if message.channel.id == main_config["game_log_sync_channel"]:
                        await send_message_to_game("Admin " + message.author.display_name, message.content)
                    if message.channel.id == main_config["game_chat_sync_channel"]:
                        if message.author.get_role(main_config["master_role"]):
                            await send_message_to_game("Admin " + message.author.display_name, message.content)
                        else:
                            await send_message_to_game(message.author.display_name, message.content)
                    else:
                        await self.wipe_manage.make_claim(message)

    async def on_member_join(self, member):
        if self.default_role is None:
            self.default_role = discord.utils.get(member.guild.roles, id=main_config["default_role_id"])
        await member.add_roles(self.default_role)
