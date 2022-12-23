# import subprocess
#
# from discord.ext import commands
#
# from chester_bot import replies
# from chester_bot.config import main_config
#
#
# @commands.command(name=main_config['short_server_name'] + "_restart_server")
# @commands.has_role(replies['master_role'])
# async def restart_server(self, ctx):
#     """Перезапускает сервер сразу"""
#     try:
#         print(
#             subprocess.check_output(
#                 f"""screen -dmS "restart_server" {main_config['short_server_name']}_restart.sh""",
#                 shell=True
#             )
#         )
#         return True
#     finally:
#         return False
