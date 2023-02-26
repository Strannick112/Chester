import codecs
import json
import os
import re

from discord.ext import commands
from chesterbot import main_config


class BotManage(commands.Cog, name="Управление ботом"):
    def __init__(self, chester_bot):
        self.chester_bot = chester_bot
        self.__replies = chester_bot.replies

    @commands.command(name=main_config['short_server_name'] + "_change_replies")
    @commands.has_role(main_config['master_role'])
    async def change_replies(self, ctx, reply: str, new_text: str):
        """
        Изменить фразы честер-бота. Принимает два параметра:
        reply: название фразы, которую нужно изменить
        new_text: новая фраза
        """
        try:
            if os.path.exists("./chesterbot/replies.json"):
                with codecs.open("./chesterbot/replies.json", "rb", encoding="utf-8") as file:
                    old_text = file.read()
                with codecs.open("./chesterbot/replies.json", "w", encoding="utf-8") as file:
                    file.write(re.sub('(' + reply + r'": ")([\w\W].+?)"', r'\1' + new_text + '"', old_text))
                self.chester_bot.reload_replies()
                await ctx.reply(self.chester_bot.__replies['change_replies_success'])
        except Exception:
            await ctx.reply(self.__replies['change_replies_fail'])
            return False
        else:
            return True

    @commands.command(name=main_config['short_server_name'] + "_get_replies_list")
    @commands.has_role(main_config['master_role'])
    async def get_replies_list(self, ctx):
        """
        Получить список фраз честер-бота.
        """
        text = json.dumps(self.__replies, ensure_ascii=False, indent=4)
        page_number = 1
        while True:
            cut = text[2000 * (page_number - 1):2000 * page_number]
            if len(cut) == 0:
                break
            else:
                await ctx.reply(f"```{cut}```")
            page_number += 1

