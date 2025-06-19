from discord.ext import tasks

from chesterbot.cogs.SavedMessage import SavedMessage


class ScreenEmbed:
    def __init__(self, name, channel, bot, head_picture, embed_list_default, view, update_callback):
        self.chester_bot = bot
        self.saved_picture_message = SavedMessage(
            name + "_picture", channel, self.chester_bot, {"file": head_picture}
        )
        self.saved_embed_message = SavedMessage(
            name, channel, self.chester_bot, {"embeds": embed_list_default, "view": view}
        )
        self.embed_list = None
        self.view = view
        self.update_callback = update_callback

    async def on_ready(self):
        await self.saved_picture_message.on_ready()
        await self.saved_embed_message.on_ready()
        self.reload_data.start()

    async def update_dashboard(self):
        try:
            await self.saved_embed_message.message.edit(embeds=self.embed_list, view=self.view)
        except:
            pass

    @tasks.loop(minutes=1)
    async def reload_data(self):
        self.embed_list = await self.update_callback()
        await self.update_dashboard()
