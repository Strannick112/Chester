import codecs
import json
import os

from discord.types.message import Message


class SavedMessage:
    def __init__(self, name, channel, bot, default_message: None):
        self.chester_bot = bot
        self.name = name
        self.channel = channel
        self.message = None
        self._message_id = None
        self.default_message = default_message if default_message is None else Message(content=f"```Данные {self.name} в обработке...```")

    async def get_message_id(self):
        if not os.path.exists(f"./chesterbot/cogs/{self.name}"):
            os.mkdir(f"./chesterbot/cogs/{self.name}")
        if not os.path.exists(f"./chesterbot/cogs/{self.name}/message.json"):
            with codecs.open(f"./chesterbot/cogs/{self.name}/message.json", "w", encoding="utf-8") as file:
                json.dump(0, file)

        with codecs.open(f"./chesterbot/cogs/{self.name}/message.json", "rb", encoding="utf-8") as file:
            return json.load(file)

    async def on_ready(self):
        self._message_id = await self.get_message_id()
        try:
            self.message = await self.channel.fetch_message(self._message_id)
        except:
            self.message = await self.channel.send(self.default_message)
            self._message_id = self.message.id
            with codecs.open(f"./chesterbot/cogs/{self.name}/message.json", "w", encoding="utf-8") as file:
                json.dump(self._message_id, file)
