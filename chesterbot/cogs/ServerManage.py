import asyncio
import select
import subprocess
import threading
import time

from discord.ext import commands
from chesterbot import main_config, ChesterBot


class ServerManage(commands.Cog, name="Управление сервером"):
    def __init__(self, chester_bot: ChesterBot):
        self.chester_bot = chester_bot
        asyncio.create_task(self.on_server_message())
        # thread = threading.Thread(target=self.on_server_message)
        # thread.start()

    @commands.command(name=main_config['short_server_name'] + "_restart_server")
    @commands.has_role(main_config['master_role'])
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
    @commands.has_role(main_config['master_role'])
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
    @commands.has_role(main_config['master_role'])
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
    @commands.has_role(main_config['master_role'])
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
    @commands.has_role(main_config['master_role'])
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
    @commands.has_role(main_config['master_role'])
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

    async def on_server_message(self):
        """Следить за сообщениями на игровом сервере"""
        f = subprocess.Popen(['tail', '-F', main_config["path_to_log"]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p = select.poll()
        p.register(f.stdout)
        channel = self.chester_bot.get_channel(main_config["game_chat_sync_channel"])
        while True:
            if p.poll(1):
                await channel.send(content=f.stdout.readline().decode())
            await asyncio.sleep(0.1)
