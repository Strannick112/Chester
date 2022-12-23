# from distutils import command
import codecs
import json
import os
import re

from discord.ext import commands

import chester_bot.bot_commands.bot_manage.help
from ... import main_config, replies, reload_replies


class BotManage(commands.Cog, name="Управление ботом"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name=main_config['short_server_name'] + "_change_replies")
    @commands.has_role(replies['master_role'])
    async def change_replies(self, ctx, reply: str, new_text: str):
        """
        Изменить фразы честер-бота. Принимает два параметра:
        reply: название фразы, которую нужно изменить
        new_text: новая фраза
        """
        try:
            if os.path.exists("./chester_bot/replies.json"):
                with codecs.open("./chester_bot/replies.json", "rb", encoding="utf-8") as file:
                    old_text = file.read()
                with codecs.open("./chester_bot/replies.json", "w", encoding="utf-8") as file:
                    file.write(re.sub('(' + reply + r'": ")([\w\W].+?)"', r'\1' + new_text + '"', old_text))
                reload_replies()
                await ctx.reply(replies['change_replies_success'])
        except Exception:
            await ctx.reply(replies['change_replies_fail'])
            return False
        else:
            return True

    @commands.command(name=main_config['short_server_name'] + "_get_replies_list")
    @commands.has_role(replies['master_role'])
    async def get_replies_list(self, ctx):
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

