import codecs
import json
import discord
from discord.ext import commands
from chester_bot.config import main_config


def reload_replies():
    with codecs.open("./chester_bot/replies.json", "r", encoding="utf-8") as file:
        global replies
        replies = json.load(file)
        replies["claim_channel_id"] = json.loads(replies["claim_channel_id"])
        replies["commands_channel_id"] = json.loads(replies["commands_channel_id"])


intents = discord.Intents.default()
intents.message_content = True
intents.members = True

with codecs.open("./chester_bot/replies.json", "r", encoding="utf-8") as file:
    replies = json.load(file)
    replies["claim_channel_id"] = json.loads(replies["claim_channel_id"])
    replies["commands_channel_id"] = json.loads(replies["commands_channel_id"])

bot = commands.Bot(command_prefix=main_config['prefix'], intents=intents)

from chester_bot.on_message import on_message
import chester_bot.bot_commands
