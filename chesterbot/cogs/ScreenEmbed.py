from discord.ext import tasks

from chesterbot.cogs.SavedMessage import SavedMessage


class ScreenEmbed:
    def __init__(self, name, channel, bot, embed_list_default, view, update_callback):
        self.chester_bot = bot
        self.saved_embed_message = SavedMessage(name, channel, self.chester_bot)
        self.saved_picture_message = SavedMessage(name + "_picture", channel, self.chester_bot)
        self.embed_list = None
        self.embed_list_default = embed_list_default
        self.view = view
        self.update_callback = update_callback

    async def on_ready(self):
        await self.saved_embed_message.on_ready()
        await self.saved_picture_message.on_ready()
        self.reload_data.start()

    async def update_dashboard(self):
        try:
            await self.saved_embed_message.message.edit(embeds=self.embed_list, view=self.view, content="")
        except:
            pass

    @tasks.loop(minutes=1)
    async def reload_data(self):
        self.embed_list = await self.update_callback()
        await self.update_dashboard()
