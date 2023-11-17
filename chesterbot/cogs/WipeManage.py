import datetime
import json
import re

import discord
from discord import WebhookMessage, Message
from discord.ext import commands

from chesterbot import wipes, main_config
from chesterbot.ConsoleDSTChecker import ConsoleDSTChecker
from chesterbot.cogs.server_manage.commands import send_message_to_game
from chesterbot.wipes import Wipe
from chesterbot.wipes.Claim import Claim
from chesterbot.wipes.Item import Item
from chesterbot.wipes.Player import Player
from chesterbot.wipes.Status import Status


class WipeManage(commands.Cog, name="Управление вайпами"):
    def __init__(self, chester_bot):
        self.chester_bot = chester_bot
        self.__replies = chester_bot.replies
        self.command_channel = None
        self.command_webhook = None

    async def on_ready(self):
        self.command_channel = self.chester_bot.get_channel(main_config["command_channel"])
        self.command_webhook = discord.utils.get(await self.command_channel.webhooks(), name='Command')
        if self.command_webhook is None:
            self.command_webhook = await self.command_channel.create_webhook(name='Command')

    @commands.command(name=main_config['short_server_name'] + "_checkout_marks_on_executed_claims")
    @commands.has_role(main_config['master_role'])
    async def checkout_marks_on_executed_claims(self, ctx):
        """Синхронизирует реакции под всеми сообщениями с заявками, хранящимися у бота"""
        for user_name, claim in wipes.last_wipe.claims.items():
            for channel_id in self.__replies['claim_channel_id']:
                async for msg in self.chester_bot \
                        .get_channel(channel_id) \
                        .history(
                    after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                ):
                    if msg.author.__str__() == user_name:
                        has_reactions = {
                            "claim_accepted_is_ok": False,
                            "claim_full_approved": False,
                            "claim_items_executed": False
                        }
                        for reaction in msg.reactions:
                            if reaction.me:
                                if reaction.__str__() == self.__replies['claim_accepted_is_ok']:
                                    has_reactions['claim_accepted_is_ok'] = True
                                if reaction.__str__() == self.__replies['claim_full_approved']:
                                    has_reactions['claim_items_executed'] = True
                                if reaction.__str__() == self.__replies['claim_items_executed']:
                                    has_reactions['claim_items_executed'] = True

                        if not has_reactions['claim_accepted_is_ok']:
                            await msg.add_reaction(self.__replies['claim_accepted_is_ok'])

                        if has_reactions['claim_full_approved']:
                            if claim.status not in (Status.approved, Status.executed):
                                msg.remove_reaction(self.__replies['claim_full_approved'], self.chester_bot.user)
                        else:
                            if claim.status in (Status.approved, Status.executed):
                                await msg.add_reaction(self.__replies['claim_full_approved'])

                        if has_reactions['claim_items_executed']:
                            if claim.status != Status.executed:
                                await msg.remove_reaction(self.__replies['claim_items_executed'], self.chester_bot.user)
                        else:
                            if claim.status == Status.executed:
                                await msg.add_reaction(self.__replies['claim_items_executed'])

        await ctx.reply(self.__replies['checkout_marks_on_executed_claims_success'])
        return True

    @commands.command(name=main_config['short_server_name'] + "_delete_claim")
    async def delete_claim(self, ctx, user_name: str = None):
        """
        Удаляет заявку пользователя.
        Администратор может указать ник пользователя, чью заявку он хочет получить. Принимает один аргумент:
        user_name: имя пользователя, чья заявка будет отправлена в чат.
        """
        cur_user = None
        if user_name is None:
            cur_user = ctx.author.__str__()
        else:
            for role in ctx.author.roles:
                if role.id == int(self.chester_bot.replies["admin_role_id"]):
                    cur_user = user_name
        if cur_user in wipes.last_wipe.claims:
            for channel_id in self.__replies['claim_channel_id']:
                async for msg in self.chester_bot \
                        .get_channel(channel_id) \
                        .history(
                    after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                ):
                    if msg.author == self.chester_bot.user:
                        continue
                    if msg.author == cur_user:
                        if (claim := self.make_claim(msg.content, msg.author, msg.created_at)) is not None \
                                and claim.equal(wipes.last_wipe.claims[cur_user]):
                            await msg.add_reaction()
            wipes.last_wipe.claims[cur_user].delete()
            del wipes.last_wipe.claims[cur_user]
            await ctx.reply(self.__replies['delete_claim_success'])
            return True
        else:
            await ctx.reply(self.__replies["delete_claim_fail"])
            return False

    @commands.command(name=main_config['short_server_name'] + "_get_claim")
    async def get_claim(self, ctx, user_name: str = None):
        """
        Отправляет заявку пользователя в чат.
        Администратор может указать ник пользователя, чью заявку он хочет получить. Принимает один аргумент:
        user_name: имя пользователя, чья заявка будет отправлена в чат.
        """
        cur_user = None
        if user_name is None:
            cur_user = ctx.author.__str__()
        else:
            for role in ctx.author.roles:
                if role.id == int(self.chester_bot.replies["admin_role_id"]):
                    cur_user = user_name
        if cur_user in wipes.last_wipe.claims:
            text = json.dumps(wipes.last_wipe.claims[cur_user], default=lambda o: o.__dict__, ensure_ascii=False,
                              indent=4)
            page_number = 1
            while True:
                cut = text[2000 * (page_number - 1):2000 * page_number]
                if len(cut) == 0:
                    break
                else:
                    await ctx.reply(f"```{cut}```")
                page_number += 1
            return True
        else:
            await ctx.reply(self.__replies["get_claim_fail"])
            return False

    async def give_items_from_game(self, dst_player_name):
        message = await self.command_webhook.send(
            content="Игрок с ником " + dst_player_name + " просит выдать вещи", wait=True,
            avatar_url=self.__replies["info_picture"]
        )
        for discord_claim_player_name, claim in wipes.last_wipe.claims.items():
            if claim.player.dst_nickname == dst_player_name:
                await self.give_items_from_discord(
                    message, discord_claim_player_name, message.created_at.__str__()
                )
                return
        else:
            await message.reply(
                content=self.__replies['give_items_fail_who_are_you'],
            )
            await message.add_reaction(self.__replies['claim_error'])
            await send_message_to_game("Chester_bot", self.__replies['give_items_fail_who_are_you'])

    @commands.command(name=main_config['short_server_name'] + "_give_items")
    async def give_items_from_discord(self, ctx, author=None, created_at=None):
        """Выдает игроку предметы на сервере по оставленной и подтверждённой заявке"""
        if author is None:
            user_name = ctx.author.__str__()
        else:
            user_name = author
        message = ctx if type(ctx) is WebhookMessage else ctx.message
        # Проверка на наличие заявки у игрока
        if user_name in wipes.last_wipe.claims:
            cur_claim = wipes.last_wipe.claims[user_name]
            # Проверка на одобренность заявки
            if cur_claim.status == Status.not_approved:
                await message.reply(
                    content="[" + main_config["server_name"] + "] @" +
                            cur_claim.player.discord_nickname + " , " +
                            self.__replies['give_items_fail_not_approved']
                )
                await message.add_reaction(self.__replies['claim_error'])
                await send_message_to_game("Chester_bot", cur_claim.player.dst_nickname + ", " + self.__replies[
                    'give_items_fail_not_approved'])
                return False
            # Проверка на выполненность заявки
            if cur_claim.status == Status.executed:
                await message.reply(
                    content="[" + main_config["server_name"] + "] @" +
                            cur_claim.player.discord_nickname + " , " +
                            self.__replies['give_items_fail_executed']
                )
                await message.add_reaction(self.__replies['claim_error'])
                await send_message_to_game("Chester_bot", cur_claim.player.dst_nickname + ", " + self.__replies[
                    'give_items_fail_executed'])
                return False
            # Проверка на наличие игрока в игре
            if not await cur_claim.player.is_player_online(self.chester_bot.console_dst_checker):
                await message.reply(
                    content="[" + main_config["server_name"] + "] @" +
                            cur_claim.player.discord_nickname + " , " +
                            self.__replies['player_is_not_online_phrase']
                )
                await message.add_reaction(self.__replies['player_is_not_online'])
                return False
            # Попытка выдать вещи
            if await cur_claim.give_items(
                    created_at if created_at is not None else message.created_at.__str__(),
                    self.chester_bot.console_dst_checker
            ):
                await message.reply(
                    content="[" + main_config["server_name"] + "] @" +
                            cur_claim.player.discord_nickname + " , " +
                            self.__replies['give_items_success']
                )
                await message.add_reaction(self.__replies['claim_items_executed'])
                await send_message_to_game("Chester_bot",
                                           cur_claim.player.dst_nickname + ", " + self.__replies['give_items_success'])
                await self.mark_claim_executed(user_name)
                return True
            else:
                await message.reply(
                    content="[" + main_config["server_name"] + "] @" +
                            cur_claim.player.discord_nickname + " , " +
                            self.__replies['give_items_fail']
                )
                await message.add_reaction(self.__replies['claim_error'])
                await send_message_to_game("Chester_bot",
                                           cur_claim.player.dst_nickname + ", " + self.__replies['give_items_fail'])
                return False
        else:
            await message.reply(
                content=self.__replies['give_items_fail_who_are_you']
            )
            await message.add_reaction(self.__replies['claim_error'])
            await send_message_to_game("Chester_bot", self.__replies['give_items_fail_who_are_you'])
            return False

    @commands.command(name=main_config['short_server_name'] + "_rollback_claim")
    @commands.has_role(main_config['master_role'])
    async def rollback_claim(self, ctx, user_name: str):
        """
        Изменяет у определённого игрока статус заявки с "Выполнена" на "Одобрена", таким образом, позволяя взять вещи
        еще раз. Принимает один аргумент: ник игрока в дискорде
        """
        if user_name in wipes.last_wipe.claims.keys():
            claim = wipes.last_wipe.claims[user_name]
            if claim.rollback_claim():
                for channel_id in self.__replies['claim_channel_id']:
                    async for msg in self.chester_bot.get_channel(channel_id).history(
                            after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                    ):
                        if msg.author.__str__() == user_name:
                            for reaction in msg.reactions:
                                if reaction.__str__() == self.__replies['claim_items_executed']:
                                    if reaction.me:
                                        await msg.remove_reaction(self.__replies['claim_items_executed'],
                                                                  self.chester_bot.user)
            await ctx.reply(self.__replies['rollback_claims_success'])
            return True
        else:
            return False

    async def approve(self, msg, cur_time):
        """
        Проверяет возможно ли изменить состояние заявки с "Не одобрена" на "Одобрена" у определённого игрока,
        и если все правила соблюдены - изменяет состояние заявки.
        Принимает один аргумент: ник игрока в дискорде
        """
        to_approve = {'bot_ok': False, 'admin_ok': False}
        for reaction in msg.reactions:
            if reaction.__str__() == self.__replies['claim_accepted_is_ok']:
                if reaction.me:
                    to_approve['bot_ok'] = True
                continue
            if reaction.__str__() == self.__replies['claim_admin_approved_is_ok']:
                async for user in reaction.users():
                    if user == self.chester_bot.user:
                        continue
                    for role in user.roles:
                        if int(self.chester_bot.replies["admin_role_id"]) == role.id:
                            to_approve['admin_ok'] = True
                            break
                continue
        if to_approve['bot_ok'] and to_approve['admin_ok']:
            wipes.last_wipe.claims[msg.author.__str__()].approve(cur_time)
            await msg.add_reaction(self.__replies['claim_full_approved'])
            return True

    @commands.command(name=main_config['short_server_name'] + "_approve_claims")
    @commands.has_role(main_config['master_role'])
    async def approve_claims(self, ctx):
        cur_time = ctx.message.created_at.__str__()
        wipes.last_wipe.stoped_at = cur_time
        wipes.last_wipe.save()
        for channel_id in self.__replies['claim_channel_id']:
            async for msg in self.chester_bot \
                    .get_channel(channel_id) \
                    .history(
                after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
            ):
                if msg.author == self.chester_bot.user:
                    continue
                if msg.author.__str__() not in wipes.last_wipe.claims.keys():
                    continue
                await self.approve(msg, cur_time)

    @commands.command(name=main_config['short_server_name'] + "_rollback_claims")
    @commands.has_role(main_config['master_role'])
    async def rollback_claims(self, ctx):
        """Изменяет у всех заявок статус "Выполнена" на "Одобрена", таким образом, позволяя взять вещи еще раз."""
        for user_name, claim in wipes.last_wipe.claims.items():
            if claim.rollback_claim():
                for channel_id in self.__replies['claim_channel_id']:
                    async for msg in self.chester_bot.get_channel(channel_id).history(
                            after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                    ):
                        if msg.author.__str__() == user_name:
                            for reaction in msg.reactions:
                                if reaction.__str__() == self.__replies['claim_items_executed']:
                                    if reaction.me:
                                        await msg.remove_reaction(self.__replies['claim_items_executed'],
                                                                  self.chester_bot.user)
        await ctx.reply(self.__replies['rollback_claims_success'])
        return True

    @commands.command(name=main_config['short_server_name'] + "_start_wipe")
    @commands.has_role(main_config['master_role'])
    async def start_wipe(self, ctx):
        """Открывает приём заявок от игроков"""
        if wipes.last_wipe.started_at == "" or wipes.last_wipe.stoped_at != "" or wipes.last_wipe.path == "./wipes/_":
            wipes.last_wipe = Wipe(
                claims={},
                server_name=main_config['server_name'],
                started_at=ctx.message.created_at.__str__(),
            )
            wipes.last_wipe.save()
            for channel_id in self.__replies['claim_channel_id']:
                async for msg in self.chester_bot \
                        .get_channel(channel_id) \
                        .history(
                    after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                ):
                    if msg.author == self.chester_bot.user:
                        continue
                    to_approve = {'approved_twice': False, 'executed': False}
                    for reaction in msg.reactions:
                        if reaction.__str__() == self.__replies['claim_full_approved']:
                            if reaction.me:
                                to_approve['approved_twice'] = True
                            continue
                        if reaction.__str__() == self.__replies['claim_items_executed']:
                            if reaction.me:
                                to_approve['executed'] = True
                            continue
                    if to_approve['approved_twice'] and not to_approve['executed']:
                        await msg.add_reaction(self.__replies['claim_is_overdue'])
            await ctx.reply(self.__replies['start_success'])
            return True
        if wipes.last_wipe.started_at != "":
            await ctx.reply(self.__replies['start_fail'])
            return False

    @commands.command(name=main_config['short_server_name'] + "_stop_wipe")
    @commands.has_role(main_config['master_role'])
    async def stop_wipe(self, ctx):
        """Закрывает набор заявок от игроков"""
        if wipes.last_wipe.stoped_at == "":
            await ctx.reply(self.__replies['stop_success'])
            await self.approve_claims(ctx)
            return True
        if wipes.last_wipe.stoped_at != "":
            await ctx.reply(self.__replies['stop_fail'])
            return False

    async def make_claim(self, message: Message):
        if raw_claim := re.findall(
                r'''Сервер: ''' + main_config['server_name']
                + r'''[\s]*?Игровой ник: ([\w\W]+?)[\s]+?Прошу:[\s]*?([\w\W]+)''',
                message.content
        ):
            loot = re.findall(r'''(\w[\w\s].+?) \("([\w].+?)"\)''', raw_claim[0][1])
            claim = Claim(
                Player(message.author.__str__(), raw_claim[0][0]),
                tuple(Item(item[0], item[1]) for item in loot),
                message.created_at.__str__(),
                wipes.last_wipe.path,
            )
            await message.add_reaction(self.__replies['claim_accepted_is_ok'])
            count_days = await claim.check_days(self.chester_bot.console_dst_checker, self.__replies['claim_days_count'])
            if count_days == 0:
                await message.add_reaction(self.__replies['claim_warning'])
            else:
                if count_days > 250:
                    await message.add_reaction(self.__replies['claim_250_days'])
            return claim
        return None

    async def mark_claim_executed(self, user_name: str):
        for channel_id in self.__replies['claim_channel_id']:
            async for msg in self.chester_bot \
                    .get_channel(channel_id) \
                    .history(
                after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
            ):
                if msg.author.__str__() == user_name:
                    for reaction in msg.reactions:
                        if reaction.__str__() == self.__replies['claim_full_approved']:
                            if reaction.me:
                                await msg.add_reaction(self.__replies['claim_items_executed'])
                                return True
        return False
