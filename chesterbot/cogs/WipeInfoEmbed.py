from discord.ext import tasks
from discord.types.embed import Embed

from chesterbot.cogs.SavedMessage import SavedMessage


class WipeInfoEmbed:
    def __init__(self, name, channel, bot, embed_default, update_callback):
        self.chester_bot = bot
        self.saved_embed_message = SavedMessage(
            name, channel, self.chester_bot, {"embeds": embed_default}
        )
        self.embed = None
        self.update_callback = update_callback

    async def on_ready(self):
        await self.saved_embed_message.on_ready()
        self.reload_data.start()

    async def update_dashboard(self):
        try:
            await self.saved_embed_message.message.edit(embeds=self.embed)
        except:
            pass

    @tasks.loop(minutes=1)
    async def reload_data(self):
        self.embed = [await self.update_callback()]
        await self.update_dashboard()
