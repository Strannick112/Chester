import codecs
import json

import discord
from discord.ext import commands

from chesterbot import main_config, wipes
from chesterbot.cogs import BotManage, WipeManage, ServerManage


class ChesterBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        with codecs.open("./chesterbot/replies.json", "r", encoding="utf-8") as file:
            self.replies = json.load(file)
            self.replies["claim_channel_id"] = json.loads(self.replies["claim_channel_id"])
            self.replies["commands_channel_id"] = json.loads(self.replies["commands_channel_id"])

        super().__init__(command_prefix=main_config['prefix'], intents=intents)

    async def init(self):
        await self.add_cog(ServerManage(self))
        await self.add_cog(BotManage(self))
        await self.add_cog(WipeManage(self))

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
        if message.author != self.user:
            if len(message.content) > 0:
                # When command
                if message.content[0] == main_config['prefix']:
                    if message.channel.id in self.replies['commands_channel_id']:
                        await self.process_commands(message)
                # When a message
                else:
                    if wipes.last_wipe.stoped_at == "":
                        author = message.author.__str__()
                        claim = WipeManage.make_claim(message.content, author, message.created_at.__str__())
                        if claim is not None:
                            wipes.last_wipe.claims[author] = claim
                            wipes.last_wipe.claims[author].save()
                            await message.add_reaction(self.replies['claim_accepted_is_ok'])
