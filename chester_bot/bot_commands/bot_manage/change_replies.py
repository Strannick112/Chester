# import codecs
# import os
# import re
#
# from discord.ext import commands
#
# from chester_bot.config import main_config
# from chester_bot import reload_replies, replies
#
#
# @commands.command(name=main_config['short_server_name'] + "_change_replies")
# @commands.has_role(replies['master_role'])
# async def change_replies(ctx, reply: str, new_text: str):
#     """
#     Изменить фразы честер-бота. Принимает два параметра:
#     reply: название фразы, которую нужно изменить
#     new_text: новая фраза
#     """
#     try:
#         if os.path.exists("./chester_bot/replies.json"):
#             with codecs.open("./chester_bot/replies.json", "rb", encoding="utf-8") as file:
#                 old_text = file.read()
#             with codecs.open("./chester_bot/replies.json", "w", encoding="utf-8") as file:
#                 file.write(re.sub('(' + reply + r'": ")([\w\W].+?)"', r'\1' + new_text + '"', old_text))
#             reload_replies()
#             await ctx.reply(replies['change_replies_success'])
#     except Exception:
#         await ctx.reply(replies['change_replies_fail'])
#         return False
#     else:
#         return True
