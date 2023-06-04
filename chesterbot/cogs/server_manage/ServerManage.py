import codecs
import os
import re
import subprocess

import discord
from discord.ext import commands, tasks

from chesterbot import main_config, ChesterBot
from chesterbot.cogs.server_manage.ServerManageView import ServerManageView
from chesterbot.cogs.server_manage.commands import restart, soft_restart, soft_stop, start, stop


class ServerManage(commands.Cog, name="Управление сервером"):
    def __init__(self, chester_bot: ChesterBot):
        self.chester_bot = chester_bot
        self.avatars = {}
        self.screen_name = main_config['short_server_name'] + main_config["worlds"][0]["shard_id"]
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
        self.__chat_file_check.start()

    @commands.command(name=main_config['short_server_name'] + "_buttons")
    @commands.has_role(main_config['master_role'])
    async def buttons(self, ctx):
        await ctx.send("Команды управления игровым сервером «" + main_config["server_name"] + "»", view=ServerManageView())

    @commands.command(name=main_config['short_server_name'] + "_restart_server")
    @commands.has_role(main_config['master_role'])
    async def restart_server(self, ctx):
        """Перезапускает сервер сразу"""
        return await restart()

    @commands.command(name=main_config['short_server_name'] + "_soft_restart_server")
    @commands.has_role(main_config['master_role'])
    async def soft_restart_server(self, ctx):
        """Перезапускает сервер через 1 минуту"""
        return await soft_restart()

    @commands.command(name=main_config['short_server_name'] + "_soft_stop_server")
    @commands.has_role(main_config['master_role'])
    async def soft_stop_server(self, ctx):
        """Останавливает сервер через 1 минуту"""
        return await soft_stop()

    @commands.command(name=main_config['short_server_name'] + "_start_server")
    @commands.has_role(main_config['master_role'])
    async def start_server(self, ctx):
        """Запускает сервер"""
        return await start()

    @commands.command(name=main_config['short_server_name'] + "_stop_server")
    @commands.has_role(main_config['master_role'])
    async def stop_server(self, ctx):
        """Останавливает сервер сразу"""
        return await stop()

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

    @tasks.loop(seconds=15)
    async def __chat_file_check(self):
        size_of_chat_file = os.path.getsize(main_config['full_path_to_server_chat_log_file'])
        if size_of_chat_file < main_config["file_chat_size"]:
            main_config["file_chat_iter"].close()
            main_config["file_chat_iter"] = codecs.open(
                main_config["full_path_to_server_chat_log_file"], "r", encoding="utf-8"
            )
            main_config["file_chat_iter"].seek(0, 2)
        main_config["file_chat_size"] = size_of_chat_file

    @tasks.loop(seconds=0.1)
    async def on_server_message(self):
        """Следить за сообщениями на игровом сервере"""
        try:
            if text := main_config["file_chat_iter"].readline()[12:-1]:
                # Блокирование цикла обратной связи
                if ':' in text:
                    if "[Announcement]" in text:
                        return
                # Обработка вариантов
                if "[Announcement]" in text:
                    await self.log_channel.send(content=("```" + text + "```"))
                    await self.chat_webhook.send(
                        content=text[14:], username="Announcement",
                        avatar_url=self.chester_bot.replies["announcement_picture"]
                    )
                    return
                if "[Leave Announcement]" in text:
                    await self.log_channel.send(content=("```" + text + "```"))
                    await self.chat_webhook.send(
                        content=self.chester_bot.replies["exit_phrase"], username="Аномалия: " + text[20:],
                        avatar_url=self.chester_bot.replies["exit_picture"]
                    )
                    return
                if "[Join Announcement]" in text:
                    await self.log_channel.send(content=("```" + text + "```"))
                    await self.chat_webhook.send(
                        content=self.chester_bot.replies["enter_phrase"], username="Аномалия: " + text[19:],
                        avatar_url=self.chester_bot.replies["enter_picture"]
                    )
                    return
                if "[Whisper]" in text:
                    await self.log_channel.send(content=("```" + text + "```"))
                if "[Say]" in text:
                    ku_id, player_name, message = re.findall(r"\[Say]\s\(([\w\W]+?)\)\s([\w\W]+):([\w\W]+)", text)[0]

                    await self.log_channel.send(content=("```" + text + "```"))
                    if message[0] != "$":
                        avatar_url = self.chester_bot.replies.get(
                            await self.chester_bot.console_dst_checker.check(
                                f"""screen -S {self.screen_name} -X stuff "c_listplayers()\n\"""",
                                ku_id + r"[\w\W]+?\<(\w+)\>",
                                main_config["worlds"][0]["shard_id"],
                                self.screen_name,
                                "unknown",
                                5
                            )
                        )
                        if "@админ" in message:
                            await self.chat_webhook.send(
                                content=re.sub(r'@админ', self.chester_bot.replies['admin_role_id'], message).strip(),
                                username=player_name,
                                avatar_url=avatar_url if avatar_url is not None else self.chester_bot.replies["unknown"]
                            )
                        elif "@дай_предметы" in message:
                            await self.chester_bot.wipe_manage.give_items_from_game(player_name)
                        else:
                            await self.chat_webhook.send(
                                content=message, username=player_name,
                                avatar_url=avatar_url if avatar_url is not None else self.chester_bot.replies["unknown"]
                            )
                    return
                await self.log_channel.send(content=("```" + text + "```"))
        except Exception as error:
            print(error)
            return
        return