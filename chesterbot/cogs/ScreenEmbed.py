import codecs
import json
import os

from discord.ext import tasks


class ScreenEmbed:
    def __init__(self, name, channel, bot, embed_list_default, view, update_callback):
        self.chester_bot = bot
        self.name = name
        self.channel = channel
        self.message = None
        self.message_id = None
        self.embed_list = None
        self.embed_list_default = embed_list_default
        self.view = view
        self.update_callback = update_callback

    async def get_message_id(self):
        if not os.path.exists(f"./chesterbot/cogs/{self.name}"):
            os.mkdir(f"./chesterbot/cogs/{self.name}")
        if not os.path.exists(f"./chesterbot/cogs/{self.name}/message.json"):
            with codecs.open(f"./chesterbot/cogs/{self.name}/message.json", "w", encoding="utf-8") as file:
                json.dump(0, file)

        with codecs.open(f"./chesterbot/cogs/{self.name}/message.json", "rb", encoding="utf-8") as file:
            return json.load(file)

    async def on_ready(self):
        self.message_id = await self.get_message_id()
        try:
            self.message = await self.channel.fetch_message(self.message_id)
        except:
            self.message = await self.channel.send(embeds=self.embed_list_default)
            self.message_id = self.message.id
            with codecs.open(f"./chesterbot/cogs/{self.name}/message.json", "w", encoding="utf-8") as file:
                json.dump(self.message_id, file)
        self.reload_data.start()

    async def update_dashboard(self):
        try:
            await self.message.edit(embeds=self.embed_list, view=self.view)
        except:
            pass

    @tasks.loop(minutes=1)
    async def reload_data(self):
        self.embed_list = await self.update_callback()
        await self.update_dashboard()
