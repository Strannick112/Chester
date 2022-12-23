# import subprocess
#
# from discord.ext import commands
#
# from chester_bot import replies
# from chester_bot.config import main_config
#
#
# @commands.command(name=main_config['short_server_name'] + "_soft_stop_server")
# @commands.has_role(replies['master_role'])
# async def soft_stop_server(self, ctx):
#     """Останавливает сервер через 1 минуту"""
#     try:
#         print(
#             subprocess.check_output(
#                 f"""screen -dmS "soft_stop_server" {main_config['short_server_name']}_soft_stop.sh""",
#                 shell=True
#             )
#         )
#         return True
#     finally:
#         return False
