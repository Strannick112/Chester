import subprocess

from discord.ext import commands

# from .restart_server import restart_server
# from .soft_restart_server import soft_restart_server
# from .soft_stop_server import soft_stop_server
# from .start_server import start_server
from .stop_server import stop_server
from .. import server_manage
from ... import main_config, replies

attrs = tuple(
    getattr(server_manage, arg)
    for arg in dir(server_manage)
    if arg[0] != '_' and callable(getattr(server_manage, arg))
)


class ServerManage(commands.Cog, name="Управление сервером"):
    def __init__(self, bot):
        self.bot = bot
        # self.name = "server_manage"

    @commands.command(name=main_config['short_server_name'] + "_restart_server")
    @commands.has_role(replies['master_role'])
    async def restart_server(self, ctx):
        """Перезапускает сервер сразу"""
        try:
            print(
                subprocess.check_output(
                    f"""screen -dmS "restart_server" {main_config['short_server_name']}_restart.sh""",
                    shell=True
                )
            )
            return True
        finally:
            return False

    @commands.command(name=main_config['short_server_name'] + "_soft_restart_server")
    @commands.has_role(replies['master_role'])
    async def soft_restart_server(self, ctx):
        """Перезапускает сервер через 1 минуту"""
        try:
            print(
                subprocess.check_output(
                    f"""screen -dmS "soft_restarting_server" {main_config['short_server_name']}_soft_restart.sh""",
                    shell=True
                )
            )
            return True
        finally:
            return False

    @commands.command(name=main_config['short_server_name'] + "_soft_stop_server")
    @commands.has_role(replies['master_role'])
    async def soft_stop_server(self, ctx):
        """Останавливает сервер через 1 минуту"""
        try:
            print(
                subprocess.check_output(
                    f"""screen -dmS "soft_stop_server" {main_config['short_server_name']}_soft_stop.sh""",
                    shell=True
                )
            )
            return True
        finally:
            return False

    @commands.command(name=main_config['short_server_name'] + "_start_server")
    @commands.has_role(replies['master_role'])
    async def start_server(self, ctx):
        """Запускает сервер"""
        try:
            print(
                subprocess.check_output(
                    f"""{main_config['short_server_name']}_start.sh""",
                    shell=True
                )
            )
            return True
        finally:
            return False

    @commands.command(name=main_config['short_server_name'] + "_start_server")
    @commands.has_role(replies['master_role'])
    async def start_server(self, ctx):
        """Запускает сервер"""
        try:
            print(
                subprocess.check_output(
                    f"""{main_config['short_server_name']}_start.sh""",
                    shell=True
                )
            )
            return True
        finally:
            return False

    @commands.command(name=main_config['short_server_name'] + "_stop_server")
    @commands.has_role(replies['master_role'])
    async def stop_server(self, ctx):
        """Останавливает сервер сразу"""
        try:
            print(
                subprocess.check_output(
                    f"""{main_config['short_server_name']}_stop.sh""",
                    shell=True
                )
            )
            return True
        finally:
            return False


# def setup(bot):
#     bot.add_cog(ServerManage(bot))


