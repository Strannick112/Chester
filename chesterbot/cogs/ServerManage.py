import re
import select
import subprocess

import discord
from discord.ext import commands, tasks
from chesterbot import main_config, ChesterBot


class ServerManage(commands.Cog, name="Управление сервером"):
    def __init__(self, chester_bot: ChesterBot):
        self.chester_bot = chester_bot
        self.file_iterator = subprocess.Popen(
            ['tail', '-F', main_config['path_to_save'] + "/" + main_config['worlds'][0]['folder_name'] + "/server_chat_log.txt"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )
        self.file_poll = select.poll()
        self.file_poll.register(self.file_iterator.stdout)
        self.chat_channel = None
        self.chat_webhook = None
        self.log_channel = None
        self.log_webhook = None

    async def on_ready(self):
        self.chat_channel = self.chester_bot.get_channel(main_config["game_chat_sync_channel"])
        self.chat_webhook = discord.utils.get(await self.chat_channel.webhooks(), name='Chat')
        if self.chat_webhook is None:
            self.chat_webhook = await self.chat_channel.create_webhook(name='Chat')
        self.log_channel = self.chester_bot.get_channel(main_config["game_log_sync_channel"])
        self.log_webhook = discord.utils.get(await self.log_channel.webhooks(), name='Log')
        if self.log_webhook is None:
            self.log_webhook = await self.log_channel.create_webhook(name='Log')
        self.on_server_message.start()

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

    @commands.command(name=main_config['short_server_name'] + "_command")
    @commands.has_role(main_config['master_role'])
    async def command(self, ctx, shard_id, *, command):
        """
        Выполняет команды на игровом сервере. Имеет два параметра:
        shard_id - уникальный ид игрового мира, на котором будет выполнена команда. 1 - поверхность, 2 - пещеры, и т д;
        command - собственно команда, которая будет передана на указанный игровой мир.
        """
        text = re.sub(r'\"', r"\"", re.sub(r'\'', r"\'", command))

        subprocess.check_output(
            f"""screen -S {main_config['short_server_name']}{shard_id} -X stuff""" +
            f""" "{text}\n\"""",
            shell=True
        )

    @tasks.loop(seconds=0.1)
    async def on_server_message(self):
        """Следить за сообщениями на игровом сервере"""
        if self.file_poll.poll(1):
            try:
                text = self.file_iterator.stdout.readline()[12:]
                if ':' in text:
                    if "[Announcement]" in text:
                        return
                if ("There are" in text and "in the world." in text) \
                   or "RemoteCommandInput: \"c_countprefabs(\"" in text:
                    return
                if "[Announcement]" in text\
                        or "[Join Announcement]" in text\
                        or "[Leave Announcement]" in text:
                    await self.chat_channel.send(content=text)
                    await self.log_channel.send(content=("```" + text + "```"))
                    return

                if "[Whisper]" in text:
                    await self.log_channel.send(content=("```" + text + "```"))

                if "[Say]" in text:
                    raw_player_info, _, message = [word.strip() for word in text.partition(':')]
                    _, player_name = raw_player_info.rsplit(' ', 1)
                    await self.log_channel.send(content=("```" + text + "```"))
                    if message[0] != "$":
                        if "@admin" in message:
                            await self.chat_webhook.send(
                                content=re.sub(r'@админ', self.chester_bot.replies['admin_role_id'], message).strip(),
                                username=player_name
                            )
                        else:
                            await self.chat_webhook.send(content=message, username=player_name)
                        return
                await self.log_channel.send(content=text)

            except Exception as error:
                print(error)
                return
        return
