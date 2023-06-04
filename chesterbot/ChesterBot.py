import codecs
import json
import re
import subprocess

import discord
from discord.ext import commands

from chesterbot import main_config, wipes
from chesterbot.ConsoleDSTChecker import ConsoleDSTChecker
from chesterbot.cogs import BotManage, WipeManage
from chesterbot.cogs.DashBoard import DashBoard
from chesterbot.cogs.server_manage import ServerManage
from chesterbot.cogs.server_manage.commands import send_message_to_game


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
        self.dashboards = tuple(DashBoard(self, world) for world in main_config['worlds'])
        self.event(self.on_ready)
        super().__init__(command_prefix=main_config['prefix'], intents=intents)

    async def on_ready(self):
        await self.user.edit(username="Chester")
        await self.server_manage.on_ready()
        await self.console_dst_checker.on_ready(self.loop)
        for dashboard in self.dashboards:
            await dashboard.on_ready()
        await self.wipe_manage.on_ready()


    async def init(self):
        # pass
        await self.add_cog(self.server_manage)
        await self.add_cog(self.bot_manage)
        await self.add_cog(self.wipe_manage)
        for dashboard in self.dashboards:
            await self.add_cog(dashboard)

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
                    if message.channel.id == main_config["game_log_sync_channel"]\
                            or message.channel.id == main_config["game_chat_sync_channel"]:
                        await send_message_to_game(message.author.display_name, message.content)
                    elif wipes.last_wipe.stoped_at == "":
                        author = message.author.__str__()
                        claim = WipeManage.make_claim(message.content, author, message.created_at.__str__())
                        if claim is not None:
                            wipes.last_wipe.claims[author] = claim
                            wipes.last_wipe.claims[author].save()
                            await message.add_reaction(self.replies['claim_accepted_is_ok'])

    async def on_member_join(self, member):
        if self.default_role is None:
            self.default_role = discord.utils.get(member.guild.roles, id=main_config["default_role_id"])
        await member.add_roles(self.default_role)
