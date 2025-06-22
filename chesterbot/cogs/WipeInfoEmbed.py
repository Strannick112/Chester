from chesterbot.cogs.MessageUtils.StreamMessage import StreamMessage


class WipeInfoEmbed:
    def __init__(self, name, channel, bot, embed_default, update_callback):
        self.chester_bot = bot
        self.stream_embed_message = StreamMessage(
            name, channel, self.chester_bot, {"embeds": embed_default}, update_callback
        )

    async def on_ready(self):
        await self.stream_embed_message.on_ready()
