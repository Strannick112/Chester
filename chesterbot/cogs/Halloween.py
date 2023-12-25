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
        if ctx.message.channel.id == self.chester_bot.replies["predictions_channel_id"]:
            random_prediction_index = random.randint(0, len(self.chester_bot.replies["predictions"]))
            stickers = self.chester_bot.replies["predictions"][random_prediction_index].get("stickers")
            await ctx.reply(
                self.chester_bot.replies["predictions"][random_prediction_index].get("text"),
                stickers=stickers,
            )
