from discord.ext import tasks

from chesterbot.cogs.MessageUtils.SavedMessage import SavedMessage


class StreamMessage:
    def __init__(self, name, channel, bot, default_message, update_callback):
        self.chester_bot = bot
        self.saved_embed_message = SavedMessage(
            name, channel, self.chester_bot, {**default_message}
        )
        self.update_callback = update_callback

    async def on_ready(self):
        await self.saved_embed_message.on_ready()
        self.reload_data.start()

    @tasks.loop(minutes=1)
    async def reload_data(self):
        try:
            await self.saved_embed_message.message.edit(**await self.update_callback())
        except:
            pass
