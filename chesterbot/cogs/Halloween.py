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

            # stickers = await ctx.message.guild.fetch_stickers()
            # for sticker in stickers:
            #     await ctx.reply(
            #         sticker.id,
            #         stickers=(await self.chester_bot.fetch_sticker(sticker.id),)
            #     )


            random_prediction_index = random.randint(
                len(self.chester_bot.replies["predictions"]) - 2,
                len(self.chester_bot.replies["predictions"]) - 1
            )
            stickers_id = self.chester_bot.replies["predictions"][random_prediction_index].get("stickers")
            if stickers_id is not None:
                stickers = (await self.chester_bot.fetch_sticker(stick_id) for stick_id in (*stickers_id,))
                await ctx.reply(
                    self.chester_bot.replies["predictions"][random_prediction_index].get("text"),
                    stickers=stickers,
                )
            else:
                await ctx.reply(
                    self.chester_bot.replies["predictions"][random_prediction_index].get("text")
                )
