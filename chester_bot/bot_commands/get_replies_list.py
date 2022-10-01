import json

from discord.ext import commands

from chester_bot import replies, bot
from chester_bot.config import main_config


@bot.command(name=main_config['short_server_name'] + "_get_replies_list")
@commands.has_role(replies['master_role'])
async def get_replies_list(ctx):
    """
    Получить список фраз честер-бота.
    """
    text = json.dumps(replies, ensure_ascii=False, indent=4)
    page_number = 1
    while True:
        cut = text[2000 * (page_number - 1):2000 * page_number]
        if len(cut) == 0:
            break
        else:
            await ctx.reply(f"```{cut}```")
        page_number += 1
