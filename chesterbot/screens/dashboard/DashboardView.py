from chesterbot.cogs.message_utils.SavedMessage import SavedMessage
from chesterbot.cogs.message_utils.StreamMessage import StreamMessage


class DashboardView:
    def __init__(self, name, channel, bot, head_picture, embed_list_default, view, update_callback):
        self.chester_bot = bot
        self.saved_picture_message = SavedMessage(
            name + "_picture", channel, self.chester_bot, {"file": head_picture}
        )
        self.stream_embed_message = StreamMessage(
            name, channel, self.chester_bot, {"embeds": embed_list_default, "view": view}, update_callback
        )

    async def on_ready(self):
        await self.saved_picture_message.on_ready()
        await self.stream_embed_message.on_ready()
