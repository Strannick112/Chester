# import subprocess
#
# from discord.ext import commands
#
# from chester_bot import replies
# from chester_bot.config import main_config
#
#
# @commands.command(name=main_config['short_server_name'] + "_start_server")
# @commands.has_role(replies['master_role'])
# async def start_server(self, ctx):
#     """Запускает сервер"""
#     try:
#         print(
#             subprocess.check_output(
#                 f"""{main_config['short_server_name']}_start.sh""",
#                 shell=True
#             )
#         )
#         return True
#     finally:
#         return False
