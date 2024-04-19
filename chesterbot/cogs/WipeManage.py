import json
import re

import discord
from discord import WebhookMessage, Message
from discord.ext import commands
from sqlalchemy import func, select

from chesterbot import main_config
from chesterbot.cogs.server_manage.commands import send_message_to_game
from chesterbot.cogs.wipe_manage.models import DiscordAccount, SteamAccount
import chesterbot.cogs.wipe_manage.models as models


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
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                print("_CHECKOUT_MARKS_ON_EXECUTED_CLAIMS")
                for claim in (await session.execute(select(
                    models.Claim
                ).where(
                    models.Claim.wipe_id == (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first().id
                ))).all():
                    print(claim)
                    print(claim.channel_id)
                    try:
                        if msg := await self.chester_bot.get_channel(claim.channel_id).fetch_message(claim.message_id):
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
                                if claim.status_id not in (models.statuses.get("approved"), models.statuses.get("executed")):
                                    msg.remove_reaction(self.__replies['claim_full_approved'], self.chester_bot.user)
                            else:
                                if claim.status_id in (models.statuses.get("approved"), models.statuses.get("executed")):
                                    await msg.add_reaction(self.__replies['claim_full_approved'])

                            if has_reactions['claim_items_executed']:
                                if claim.status_id != models.statuses.get("executed"):
                                    await msg.remove_reaction(self.__replies['claim_items_executed'], self.chester_bot.user)
                            else:
                                if claim.status_id == models.statuses.get("executed"):
                                    await msg.add_reaction(self.__replies['claim_items_executed'])
                    except Exception as error:
                        print(error)

        await ctx.reply(self.__replies['checkout_marks_on_executed_claims_success'])
        return True

    @commands.command(name=main_config['short_server_name'] + "_delete_claim")
    async def delete_claim(self, ctx, discord_id: str = None):
        """
        Удаляет заявку пользователя.
        Администратор может указать ник пользователя, чью заявку он хочет удалить. Принимает один аргумент:
        user_name: имя пользователя, чья заявка будет отправлена в чат.
        """
        try:
            if discord_id is not None:
                discord_id = int(discord_id)
        except:
            ctx.reply("Параметры команды указаны не верно")
        requested_discord_id = None
        if discord_id is None:
            requested_discord_id = ctx.author.id
        else:
            for role in ctx.author.roles:
                if role.id == int(self.chester_bot.replies["admin_role_id"]):
                    requested_discord_id = discord_id
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                if claim := await self.get_claim_by_discord_id(requested_discord_id, session=session):
                    try:
                        if msg := await self.chester_bot.get_channel(claim.channel_id).fetch_message(claim.message_id):
                            await msg.add_reaction(self.__replies['claim_deleted'])
                    except Exception as error:
                        print(error)
                    await session.delete(claim)
                    await ctx.reply(self.__replies['delete_claim_success'])
                    return True
                else:
                    await ctx.reply(self.__replies["delete_claim_fail"])
                    return False

    @commands.command(name=main_config['short_server_name'] + "_get_claim")
    async def get_claim(self, ctx, discord_id: str = None):
        """
        Отправляет информацию о заявке в чат.
        Администратор может указать уникальный идентификатор пользователя, заявку которого он хочет получить. Принимает один аргумент:
        discord_id: id пользователя, чья заявка будет отправлена в чат.
        """
        try:
            if discord_id is not None:
                discord_id = int(discord_id)
        except:
            await ctx.reply("Параметры команды указаны не верно")
        requested_discord_id = None
        if discord_id is None:
            requested_discord_id = ctx.author.id
        else:
            for role in ctx.author.roles:
                if role.id == int(self.chester_bot.replies["admin_role_id"]):
                    requested_discord_id = discord_id
                    break
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                if claim := await self.get_claim_by_discord_id(requested_discord_id, session=session):
                    text = await claim.to_str()
        if text is not None:
            await ctx.reply(embed=discord.Embed(
                title="Информация о заявке",
                description=text,
                colour=discord.Colour.dark_teal()
            ))
            # page_number = 1
            # while True:
            #     cut = text[2000 * (page_number - 1):2000 * page_number]
            #     if len(cut) == 0:
            #         break
            #     else:
            #         await ctx.reply(f"```json\n{cut}```")
            #     page_number += 1
            return True
        else:
            await ctx.reply(self.__replies["get_claim_fail"])
            return False

    @commands.command(name=main_config['short_server_name'] + "_wipe_info")
    async def wipe_info(self, ctx, wipe_id: str = None):
        """
        Отправляет информацию о вайпе в чат.
        Администратор может указать номер вайпа, информацию о котором он хочет получить. Принимает один аргумент:
        wipe_id: номер вайпа, информация о котором будет отправлена в чат.
        """
        try:
            async with self.chester_bot.async_session() as session:
                async with session.begin():
                    if wipe_id is None:
                        if last_wipe := (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first():
                            text = await last_wipe.to_str()
                    else:
                        wipe_id = int(wipe_id)
                        if last_wipe := (await session.execute(select(models.Wipe).filter_by(id=wipe_id))).scalars().first():
                            text = await last_wipe.to_str()
            await ctx.reply(embed=discord.Embed(
                title="Информация о вайпе",
                description=text,
                colour=discord.Colour.dark_teal()
            ))
            return True
        except:
            await ctx.reply("Параметры команды указаны не верно")


    @commands.command(name=main_config['short_server_name'] + "_wipe_list")
    async def wipe_list(self, ctx):
        """
        Отправляет информацию о всех вайпах в чат.
        """
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                embed = discord.Embed(
                    title="Информация о вайпах",
                    colour=discord.Colour.dark_teal()
                )
                for index, wipe in enumerate((await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().all()):
                    stopped = '?' if wipe.stopped == wipe.started else str(wipe.stopped)
                    embed.add_field(name="", value=f"{index + 1}. Начало={wipe.started}, Конец={stopped}", inline=False)

        await ctx.reply(embed=embed)
        return True

    async def give_items_from_game(self, steam_nickname):
        message = await self.command_webhook.send(
            content="Игрок с ником " + steam_nickname + " просит выдать вещи", wait=True,
            avatar_url=self.__replies["info_picture"]
        )
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                if claim := await self.get_claim_by_steam_nickname(steam_nickname, session):
                    discord_id = await claim.get_discord_id()
        if discord_id:
            await self.give_items_from_discord(message, discord_id)
            return
        else:
            await message.reply(
                content=self.__replies['give_items_fail_who_are_you'],
            )
            await message.add_reaction(self.__replies['claim_error'])
            await send_message_to_game("Chester_bot", self.__replies['give_items_fail_who_are_you'])

    @commands.command(name=main_config['short_server_name'] + "_give_items")
    async def give_items_from_discord(self, ctx, discord_id=None):
        """
        Выдает игроку предметы на сервере по оставленной и подтверждённой заявке
        Администратор может выполнить эту команду от имени любого другого игрока.
        Параметры:
        discord_id: уникальный целочисленный ид пользователя в дискорде
        """
        try:
            if discord_id is not None:
                discord_id = int(discord_id)
        except:
            await ctx.reply("Параметры команды указаны не верно")
        if discord_id is None:
            discord_id = ctx.author.id
        message = ctx if type(ctx) is WebhookMessage else ctx.message

        try:
            status_id = None
            print("meaw-3")
            # Проверка на наличие заявки у игрока
            async with self.chester_bot.async_session() as session:
                async with session.begin():
                    if claim := await self.get_claim_by_discord_id(discord_id=discord_id, session=session):
                        status_id = claim.status_id
                        print("meaw-5")
                        steam_nickname = await claim.get_steam_nickname()
                        channel_id = claim.channel_id
                        message_id = claim.message_id
                        print("meaw-4")
                        is_player_online = not await (
                            await claim.awaitable_attrs.player
                        ).is_player_online(self.chester_bot.console_dst_checker)
            print("meaw-2")
            if status_id is not None:
                discord_id = str(discord_id)

                # Проверка на одобренность заявки
                if status_id == models.statuses.get("not_approved"):

                    await message.reply(
                        content="[" + main_config["server_name"] + "] <@" +
                                discord_id + "> , " +
                                self.__replies['give_items_fail_not_approved']
                    )
                    await message.add_reaction(self.__replies['claim_error'])
                    await send_message_to_game("Chester_bot", steam_nickname + ", " + self.__replies[
                        'give_items_fail_not_approved']
                    )
                    return False

                # Проверка на выполненность заявки
                if status_id == models.statuses.get("executed"):
                    await message.reply(
                        content="[" + main_config["server_name"] + "] <@" +
                                discord_id + "> , " +
                                self.__replies['give_items_fail_executed']
                    )
                    await message.add_reaction(self.__replies['claim_error'])
                    await send_message_to_game("Chester_bot", steam_nickname + ", " + self.__replies[
                        'give_items_fail_executed'])
                    return False

                # Проверка на наличие игрока в игре
                if is_player_online:
                    await message.reply(
                        content="[" + main_config["server_name"] + "] <@" +
                                discord_id + "> , " +
                                self.__replies['player_is_not_online_phrase']
                    )
                    await message.add_reaction(self.__replies['player_is_not_online'])
                    return False
                # Попытка выдать вещи
                print("meaw-1")
                async with self.chester_bot.async_session() as session:
                    async with session.begin():
                        if await (
                            await self.get_claim_by_discord_id(discord_id=int(discord_id), session=session)
                        ).give_items(
                            session=session,
                            console_dst_checker=self.chester_bot.console_dst_checker
                        ):
                            await message.reply(
                                content="[" + main_config["server_name"] + "] <@" +
                                        discord_id + "> , " +
                                        self.__replies['give_items_success']
                            )
                            await message.add_reaction(self.__replies['claim_items_executed'])
                            await send_message_to_game("Chester_bot",
                                                       steam_nickname + ", " + self.__replies['give_items_success'])
                            await self.mark_claim_executed(channel_id=channel_id, message_id=message_id)
                            return True
                        else:
                            await message.reply(
                                content="[" + main_config["server_name"] + "] <@" +
                                        discord_id + "> , " +
                                        self.__replies['give_items_fail']
                            )
                            await message.add_reaction(self.__replies['claim_error'])
                            await send_message_to_game("Chester_bot",
                                                       steam_nickname + ", " + self.__replies['give_items_fail'])
                            return False
        except Exception as error:
            print(error)
        await message.reply(
            content=self.__replies['give_items_fail_who_are_you']
        )
        await message.add_reaction(self.__replies['claim_error'])
        await send_message_to_game("Chester_bot", self.__replies['give_items_fail_who_are_you'])
        return False

    @commands.command(name=main_config['short_server_name'] + "_rollback_claim")
    @commands.has_role(main_config['master_role'])
    async def rollback_claim(self, ctx, discord_id: str):
        """
        Изменяет у определённого игрока статус заявки с "Выполнена" на "Одобрена", таким образом, позволяя взять вещи
        еще раз. Принимает один аргумент: ник игрока в дискорде
        """
        try:
            if discord_id is not None:
                discord_id = int(discord_id)
        except:
            await ctx.reply("Параметры команды указаны не верно")
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                if claim := await self.get_claim_by_discord_id(discord_id=discord_id, session=session):
                    if await claim.rollback_claim(session=session):
                        try:
                            if msg := await self.chester_bot.get_channel(claim.channel_id).fetch_message(claim.message_id):
                                for reaction in msg.reactions:
                                    if reaction.__str__() == self.__replies['claim_items_executed']:
                                        if reaction.me:
                                            await msg.remove_reaction(self.__replies['claim_items_executed'],
                                                                      self.chester_bot.user)

                                await ctx.reply(self.__replies['rollback_claim_success'])
                                return True
                        except Exception as error:
                            print(error)
                    else:
                        await ctx.reply(self.__replies['rollback_claim_fall'])

    async def approve(self, msg, claim, session):
        """
        Проверяет возможно ли изменить состояние заявки с "Не одобрена" на "Одобрена" у определённого игрока,
        и если все правила соблюдены - изменяет состояние заявки.
        Принимает один аргумент: ник игрока в дискорде
        """
        print("APPROVE")
        to_approve = {'bot_ok': False, 'admin_ok': False}
        try:
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
                print("APPROVE_2")
                await claim.approve(session=session)
                await msg.add_reaction(self.__replies['claim_full_approved'])
                return True
        except Exception as error:
            print(error)

    @commands.command(name=main_config['short_server_name'] + "_rollback_claims")
    @commands.has_role(main_config['master_role'])
    async def rollback_claims(self, ctx):
        """Изменяет у всех заявок статус "Выполнена" на "Одобрена", таким образом, позволяя взять вещи еще раз."""
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                for claim in (await session.execute(select(models.Claim).where(
                    models.Wipe.id == (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first().id
                ))).scalars().all():
                    if await claim.rollback_claim(session=session):
                        try:
                            if msg := await self.chester_bot.get_channel(claim.channel_id).fetch_message(claim.message_id):
                                for reaction in msg.reactions:
                                    if reaction.__str__() == self.__replies['claim_items_executed']:
                                        if reaction.me:
                                            await msg.remove_reaction(self.__replies['claim_items_executed'],
                                                                      self.chester_bot.user)
                        except Exception as error:
                            print(error)
        await ctx.reply(self.__replies['rollback_claims_success'])
        return True

    @commands.command(name=main_config['short_server_name'] + "_start_wipe")
    @commands.has_role(main_config['master_role'])
    async def start_wipe(self, ctx):
        """Открывает приём заявок от игроков"""
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                last_wipe = (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first()
                if last_wipe.started != last_wipe.stopped:
                    last_wipe = models.Wipe()
                    session.add(last_wipe)
                    for claim in (await session.execute(select(
                        models.Claim
                    ).where(
                        models.Claim.wipe_id == (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first().id
                    ))).scalars().all():
                        try:
                            if msg := await self.chester_bot.get_channel(claim.channel_id).fetch_message(claim.message_id):
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
                        except Exception as error:
                            print(error)
                    await ctx.reply(self.__replies['start_success'])
                    return True
                else:
                    await ctx.reply(self.__replies['start_fail'])
                    return False

    @commands.command(name=main_config['short_server_name'] + "_stop_wipe")
    @commands.has_role(main_config['master_role'])
    async def stop_wipe(self, ctx):
        """Закрывает набор заявок от игроков"""
        async with self.chester_bot.async_session() as session:
            async with session.begin():
        # if True:
                last_wipe = (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first()
                is_started = last_wipe.stopped == last_wipe.started
                if is_started:
                    await ctx.reply(self.__replies['stop_success'])
                    last_wipe.stopped = func.now()
                    for claim in (await session.execute(select(models.Claim).where(
                            models.Wipe.id == (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first().id
                    ))).scalars().all():
                        try:
                            if msg := await self.chester_bot.get_channel(claim.channel_id).fetch_message(claim.message_id):
                                await self.approve(msg, claim, session)
                        except Exception as error:
                            print(error)
                    return True
                else:
                    await ctx.reply(self.__replies['stop_fail'])
                    return False

    async def make_claim(self, message: Message):
        # Проверка на открытость вайпа
        if message.channel.id in self.__replies['claim_channel_id']:
            async with self.chester_bot.async_session() as session:
                async with session.begin():
                    last_wipe = (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first()
                    if last_wipe.stopped != last_wipe.started:
                        return
            if raw_claim := re.findall(
                r'''Сервер: ''' + main_config['server_name']
                + r'''[\s]*?Игровой ник: ([\w\W]+?)\sИдентификатор:\s(.+?)\sПрошу:[\s]*?([\w\W]+)''',
                    message.content
            ):
                loot = re.findall(r'''([\w\s]+?)\s*\(\"([\w]+?)\"\)''', raw_claim[0][2])
                async with self.chester_bot.async_session() as session:
                    async with session.begin():
                        discord_account = await DiscordAccount.get_or_create(
                            session=session,
                            discord_id=message.author.id,
                            name=message.author.name,
                            display_name=message.author.display_name
                        )
                        await session.flush()
                        steam_account = await SteamAccount.get_or_create(
                            session=session,
                            ku_id=raw_claim[0][1],
                            nickname=raw_claim[0][0]
                        )
                        await session.flush()
                        player = await models.Player.get_or_create(
                            session=session,
                            discord_account_id=discord_account.id,
                            steam_account_id=steam_account.id
                        )
                        await session.flush()
                        items = [
                            await models.Item.get_or_create(session=session, name=item[0].strip(), console_id=item[1])
                            for item in loot
                        ]
                        await session.flush()
                        numbered_items = [
                            await models.NumberedItem.get_or_create(session=session, number=number, item_id=item.id)
                            for number, item in enumerate(items)
                        ]
                        claim = await models.Claim.get_or_create(
                            session=session,
                            message_id=message.id,
                            message_link=message.jump_url,
                            channel_id=message.channel.id,
                            player_id=player.id,
                            numbered_items=numbered_items,
                            wipe_id=last_wipe.id,
                            revoke=self.revoke_reactions
                        )
                        await session.flush()
                        await message.add_reaction(self.__replies['claim_accepted_is_ok'])
                        count_days = await claim.check_days(console_dst_checker=self.chester_bot.console_dst_checker)
                        await session.commit()
                await self.sync_reactions(count_days, message)
            else:
                await message.add_reaction(self.__replies['claim_warning'])

    async def check_claim(self, dst_player_name):
        await send_message_to_game(
            "",
            "Обновление информации о заявке принято к исполнению"
        )
        async with self.chester_bot.async_session() as session:
            async with session.begin():
                if claim := await self.get_claim_by_steam_nickname(dst_player_name, session):
                    try:
                        if msg := await self.chester_bot.get_channel(claim.channel_id).fetch_message(claim.message_id):
                            count_days = await claim.check_days(console_dst_checker=self.chester_bot.console_dst_checker)
                            await self.sync_reactions(count_days, msg)
                            return
                    except Exception as error:
                        print(error)
        await send_message_to_game(
            "",
            "Заявка не обнаружена, обратитесь к администратору"
        )

    async def sync_reactions(self, count_days, msg):
        try:
            if count_days == 0:
                await msg.add_reaction(self.__replies['claim_warning'])
            else:
                try:
                    await msg.remove_reaction(self.__replies['claim_warning'], self.chester_bot.user)
                finally:
                    for day, reaction in self.__replies["claim_days_count"].items():
                        if count_days > int(day):
                            await msg.add_reaction(reaction)
        except Exception as error:
            print(error)

    async def mark_claim_executed(self, channel_id, message_id):
        try:
            if msg := await self.chester_bot.get_channel(channel_id).fetch_message(message_id):
                for reaction in msg.reactions:
                    if reaction.__str__() == self.__replies['claim_full_approved']:
                        if reaction.me:
                            await msg.add_reaction(self.__replies['claim_items_executed'])
                            return True
            return False
        except Exception as error:
            print(error)

    async def get_claim_by_steam_nickname(self, steam_nickname, session):
        return (await session.execute(select(
            models.Claim
        ).join(models.Claim.player
        ).join(models.Player.steam_account
        ).where(
            models.Claim.wipe_id == (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first().id
        ).where(
            models.SteamAccount.nickname == steam_nickname
        ))).scalars().first()

    async def get_claim_by_discord_id(self, discord_id, session):
        return (await session.execute(select(
            models.Claim
        ).join(
            models.Claim.player
        ).join(
            models.Player.discord_account
        ).where(
            models.Claim.wipe_id == (await session.execute(select(models.Wipe).order_by(models.Wipe.id.desc()))).scalars().first().id
        ).where(
            models.DiscordAccount.discord_id == discord_id
        ))).scalars().first()

    async def revoke_reactions(self, player_id, session):
        if claim := await self.get_claim_by_discord_id(
            (
                await (
                    await session.execute(select(models.Player).filter_by(id=player_id))
                ).scalars().first().awaitable_attrs.discord_account
            ).discord_id,
            session=session
        ):
            try:
                if msg := await self.chester_bot.get_channel(claim.channel_id).fetch_message(claim.message_id):
                    for reaction in msg.reactions:
                        if reaction.me:
                            await reaction.remove(self.chester_bot.user)
                        continue
                    await msg.add_reaction(self.__replies["claim_deleted"])
            except Exception as error:
                print(error)
        return claim
