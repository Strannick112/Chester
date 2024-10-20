import random

from discord.ext import commands
from chesterbot import main_config


class Halloween(commands.Cog, name="Хеллоуин"):
    def __init__(self, chester_bot):
        self.chester_bot = chester_bot
        self.__replies = chester_bot.replies
        self.__weights = tuple(
            weight if (weight := prediction.get("weight")) is not None
            else 1
            for prediction in self.chester_bot.replies["predictions"]
        )

    @commands.command(name="magic")
    async def magic(self, ctx):
        """
        Узнать предсказание на сегодня.
        """
        if main_config["is_event"]:
            if ctx.message.channel.id == self.chester_bot.replies["predictions_channel_id"]:
                prediction = random.choices(self.chester_bot.replies["predictions"], weights=self.__weights, k=1)[0]
                stickers_id = prediction.get("stickers")
                if stickers_id is not None:
                    stickers = [await self.chester_bot.fetch_sticker(stick_id) for stick_id in (*stickers_id,)]
                    await ctx.reply(
                        prediction.get("text"),
                        stickers=stickers,
                    )
                else:
                    await ctx.reply(
                        prediction.get("text")
                    )
