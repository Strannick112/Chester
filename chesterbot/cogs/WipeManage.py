import datetime
import json
import re

from discord.ext import commands

from chesterbot import wipes, main_config
from chesterbot.wipes import Wipe
from chesterbot.wipes.Claim import Claim
from chesterbot.wipes.Item import Item
from chesterbot.wipes.Player import Player
from chesterbot.wipes.Status import Status


class WipeManage(commands.Cog, name="Управление вайпами"):
    def __init__(self, chester_bot):
        self.bot = chester_bot
        self.__replies = chester_bot.replies

    @commands.command(name=main_config['short_server_name'] + "_checkout_marks_on_executed_claims")
    @commands.has_role(main_config['master_role'])
    async def checkout_marks_on_executed_claims(self, ctx):
        """Синхронизирует реакции под всеми сообщениями с заявками, хранящимися у бота"""
        for user_name, claim in wipes.last_wipe.claims.items():
            for channel_id in self.__replies['claim_channel_id']:
                async for msg in self.bot \
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
                                msg.remove_reaction(self.__replies['claim_full_approved'], self.bot.user)
                        else:
                            if claim.status in (Status.approved, Status.executed):
                                await msg.add_reaction(self.__replies['claim_full_approved'])

                        if has_reactions['claim_items_executed']:
                            if claim.status != Status.executed:
                                await msg.remove_reaction(self.__replies['claim_items_executed'], self.bot.user)
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
                if role.__str__() == main_config['master_role']:
                    cur_user = user_name
        if cur_user in wipes.last_wipe.claims:
            for channel_id in self.__replies['claim_channel_id']:
                async for msg in self.bot \
                        .get_channel(channel_id) \
                        .history(
                    after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                ):
                    if msg.author == self.bot.user:
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
                if role.__str__() == main_config['master_role']:
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

    @commands.command(name=main_config['short_server_name'] + "_give_items")
    async def give_items(self, ctx):
        """Выдает игроку предметы на сервере по оставленной и подтверждённой заявке"""
        user_name = ctx.author.__str__()
        if user_name in wipes.last_wipe.claims:
            cur_claim = wipes.last_wipe.claims[user_name]
            if cur_claim.status == Status.not_approved:
                await ctx.reply(self.__replies['give_items_fail_not_approved'])
                await ctx.message.add_reaction(self.__replies['claim_error'])
                return False
            if cur_claim.status == Status.executed:
                await ctx.reply(self.__replies['give_items_fail_executed'])
                await ctx.message.add_reaction(self.__replies['claim_error'])
                return False
            if cur_claim.give_items(ctx.message.created_at.__str__()):
                await ctx.reply(self.__replies['give_items_success'])
                await ctx.message.add_reaction(self.__replies['claim_items_executed'])
                await self.mark_claim_executed(user_name)
                return True
            else:
                await ctx.reply(self.__replies['give_items_fail'])
                await ctx.message.add_reaction(self.__replies['claim_error'])
                return False
        else:
            await ctx.reply(self.__replies['give_items_fail_who_are_you'])
            await ctx.message.add_reaction(self.__replies['claim_error'])
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
                    async for msg in self.bot.get_channel(channel_id).history(
                            after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                    ):
                        if msg.author.__str__() == user_name:
                            for reaction in msg.reactions:
                                if reaction.__str__() == self.__replies['claim_items_executed']:
                                    if reaction.me:
                                        await msg.remove_reaction(self.__replies['claim_items_executed'], self.bot.user)
            await ctx.reply(self.__replies['rollback_claims_success'])
            return True
        else:
            return False

    @commands.command(name=main_config['short_server_name'] + "_rollback_claims")
    @commands.has_role(main_config['master_role'])
    async def rollback_claims(self, ctx):
        """Изменяет у всех заявок статус "Выполнена" на "Одобрена", таким образом, позволяя взять вещи еще раз."""
        for user_name, claim in wipes.last_wipe.claims.items():
            if claim.rollback_claim():
                for channel_id in self.__replies['claim_channel_id']:
                    async for msg in self.bot.get_channel(channel_id).history(
                            after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                    ):
                        if msg.author.__str__() == user_name:
                            for reaction in msg.reactions:
                                if reaction.__str__() == self.__replies['claim_items_executed']:
                                    if reaction.me:
                                        await msg.remove_reaction(self.__replies['claim_items_executed'], self.bot.user)
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
                async for msg in self.bot \
                        .get_channel(channel_id) \
                        .history(
                    after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                ):
                    if msg.author == self.bot.user:
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
            cur_time = ctx.message.created_at.__str__()
            wipes.last_wipe.stoped_at = cur_time
            wipes.last_wipe.save()
            for channel_id in self.__replies['claim_channel_id']:
                async for msg in self.bot \
                        .get_channel(channel_id) \
                        .history(
                    after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
                ):
                    if msg.author == self.bot.user:
                        continue
                    if msg.author.__str__() not in wipes.last_wipe.claims.keys():
                        continue
                    to_approve = {'bot_ok': False, 'admin_ok': False}
                    for reaction in msg.reactions:
                        if reaction.__str__() == self.__replies['claim_accepted_is_ok']:
                            if reaction.me:
                                to_approve['bot_ok'] = True
                            continue
                        if reaction.__str__() == self.__replies['claim_admin_approved_is_ok']:
                            async for user in reaction.users():
                                if user == self.bot.user:
                                    continue
                                for role in user.roles:
                                    if main_config['master_role'] == role.name:
                                        to_approve['admin_ok'] = True
                                        break
                            continue
                    if to_approve['bot_ok'] and to_approve['admin_ok']:
                        wipes.last_wipe.claims[msg.author.__str__()].approve(cur_time)
                        await msg.add_reaction(self.__replies['claim_full_approved'])
            return True
        if wipes.last_wipe.stoped_at != "":
            await ctx.reply(self.__replies['stop_fail'])
            return False

    @staticmethod
    def make_claim(text: str, author: str, created_at: str):
        if message := re.findall(
                r'''Сервер: ''' + main_config['server_name']
                + r'''[\s]*?Игровой ник: ([\w\W]+?)[\s]+?Прошу:[\s]*?([\w\W]+)''',
                text
        ):
            loot = re.findall(r'''(\w[\w\s].+?) \("([\w].+?)"\)''', message[0][1])
            print(f"Игровой ник: {message[0][0]}")
            for item in loot:
                print(f"Игровое название предмета: {item[0]}")
                print(f"Код для консоли: {item[1]}")
            return Claim(
                Player(author, message[0][0]),
                tuple(Item(item[0], item[1]) for item in loot),
                created_at,
                wipes.last_wipe.path,
            )
        return None

    async def mark_claim_executed(self, user_name: str):
        for channel_id in self.__replies['claim_channel_id']:
            async for msg in self.bot \
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
