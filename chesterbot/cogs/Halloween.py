import codecs
import json
import os
import random
import re

from discord.ext import commands
from chesterbot import main_config


class Halloween(commands.Cog, name="Хеллоуин"):
    def __init__(self, chester_bot):
        self.chester_bot = chester_bot
        self.__replies = chester_bot.replies
    @commands.command(name="magic")
    async def change_replies(self, ctx):
        """
        Узнать предсказание на сегодня.
        """
        if main_config["is_event"] and ctx.message.channel.id == self.chester_bot.replies["predictions_channel_id"]:
            await ctx.reply(random.choice(self.chester_bot.replies["predictions"]))
