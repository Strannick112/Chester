import codecs
import datetime
import json
import os.path

import discord
from discord.ext import commands
import re

import wipes
from config import main_config
from wipes import Wipe
from wipes.Claim import Claim
from wipes.Item import Item
from wipes.Player import Player
from wipes.Status import Status

intents = discord.Intents.default()
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix=main_config['prefix'], intents=intents)

with codecs.open("./replies.json", "r", encoding="utf-8") as file:
    replies = json.load(file)
    replies["claim_channel_id"] = int(replies["claim_channel_id"])
    replies["commands_channel_id"] = json.loads(replies["commands_channel_id"])


@bot.command(name=main_config['short_server_name'] + "_start_claims")
@commands.has_role(replies['master_role'])
async def start_wipe(ctx):
    """Открывает приём заявок от игроков"""
    if wipes.last_wipe.started_at == "" or wipes.last_wipe.stoped_at != "" or wipes.last_wipe.path == "./wipes/_":
        wipes.last_wipe = Wipe(main_config['server_name'], ctx.message.created_at.__str__(), claims={})
        wipes.last_wipe.save()
        async for msg in bot \
                .get_channel(replies['claim_channel_id']) \
                .history(
            after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
        ):
            if msg.author == bot.user:
                continue
            to_approve = {'approved_twice': False, 'executed': False}
            for reaction in msg.reactions:
                if reaction.__str__() == replies['claim_full_approved']:
                    if reaction.me:
                        to_approve['approved_twice'] = True
                    continue
                if reaction.__str__() == replies['claim_items_executed']:
                    if reaction.me:
                        to_approve['executed'] = True
                    continue
            if to_approve['approved_twice'] and not to_approve['executed']:
                await msg.add_reaction(replies['claim_is_overdue'])
        await ctx.reply(replies['start_success'])
        return True
    if wipes.last_wipe.started_at != "":
        await ctx.reply(replies['start_fail'])
        return False


@bot.command(name=main_config['short_server_name'] + "_stop_claims")
@commands.has_role(replies['master_role'])
async def stop_wipe(ctx):
    """Закрывает набор заявок от игроков"""
    if wipes.last_wipe.stoped_at == "":
        await ctx.reply(replies['stop_success'])
        cur_time = ctx.message.created_at.__str__()
        wipes.last_wipe.stoped_at = cur_time
        wipes.last_wipe.save()
        async for msg in bot \
                .get_channel(replies['claim_channel_id']) \
                .history(
            after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
        ):
            if msg.author == bot.user:
                continue
            to_approve = {'bot_ok': False, 'admin_ok': False}
            for reaction in msg.reactions:
                if reaction.__str__() == replies['claim_accepted_is_ok']:
                    if reaction.me:
                        to_approve['bot_ok'] = True
                    continue
                if reaction.__str__() == replies['claim_admin_approved_is_ok']:
                    async for user in reaction.users():
                        if user == bot.user:
                            continue
                        for role in user.roles:
                            if replies['master_role'] == role.name:
                                to_approve['admin_ok'] = True
                                break
                    continue
            if to_approve['bot_ok'] and to_approve['admin_ok']:
                wipes.last_wipe.claims[msg.author.__str__()].approve(cur_time)
                await msg.add_reaction(replies['claim_full_approved'])
        return True
    if wipes.last_wipe.stoped_at != "":
        await ctx.reply(replies['stop_fail'])
        return False


async def mark_claim_executed(user_name: str):
    async for msg in bot \
            .get_channel(replies['claim_channel_id']) \
            .history(
        after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
    ):
        if msg.author.__str__() == user_name:
            for reaction in msg.reactions:
                if reaction.__str__() == replies['claim_full_approved']:
                    if reaction.me:
                        await msg.add_reaction(replies['claim_items_executed'])
                        return True
    return False


def reload_replies():
    with codecs.open("./replies.json", "r", encoding="utf-8") as file:
        global replies
        replies = json.load(file)
        replies["claim_channel_id"] = int(replies["claim_channel_id"])
        replies["commands_channel_id"] = json.loads(replies["commands_channel_id"])


@bot.command(name=main_config['short_server_name'] + "_give_items")
async def give_items(ctx):
    """Выдает игроку предметы на сервере по оставленной и подтверждённой заявке"""
    user_name = ctx.author.__str__()
    if user_name in wipes.last_wipe.claims:
        cur_claim = wipes.last_wipe.claims[user_name]
        if cur_claim.status == Status.not_approved:
            await ctx.reply(replies['give_items_fail_not_approved'])
            await ctx.message.add_reaction(replies['claim_error'])
            return False
        if cur_claim.status == Status.executed:
            await ctx.reply(replies['give_items_fail_executed'])
            await ctx.message.add_reaction(replies['claim_error'])
            return False
        if cur_claim.give_items(ctx.message.created_at.__str__()):
            await ctx.reply(replies['give_items_success'])
            await ctx.message.add_reaction(replies['claim_items_executed'])
            await mark_claim_executed(user_name)
            return True
        else:
            await ctx.reply(replies['give_items_fail'])
            await ctx.message.add_reaction(replies['claim_error'])
            return False
    else:
        await ctx.reply(replies['give_items_fail_who_are_you'])
        await ctx.message.add_reaction(replies['claim_error'])
        return False


@bot.command(name=main_config['short_server_name'] + "_change_replies")
@commands.has_role(replies['master_role'])
async def change_replies(ctx, reply: str, new_text: str):
    """
    Изменить фразы честер-бота. Принимает два параметра:
    reply: название фразы, которую нужно изменить
    new_text: новая фраза
    """
    try:
        if os.path.exists("./replies.json"):
            with codecs.open("./replies.json", "rb", encoding="utf-8") as file:
                old_text = file.read()
            with codecs.open("./replies.json", "w", encoding="utf-8") as file:
                file.write(re.sub('(' + reply + r'": ")([\w\W].+?)"', r'\1' + new_text + '"', old_text))
            reload_replies()
            await ctx.reply(replies['change_replies_success'])
    except Exception:
        await ctx.reply(replies['change_replies_fail'])
        return False
    else:
        return True


@bot.command(name=main_config['short_server_name'] + "_get_replies_list")
@commands.has_role(replies['master_role'])
async def get_replies_list(ctx):
    """
    Получить список фраз честер-бота.
    """
    text = json.dumps(replies, ensure_ascii=False, indent=4)
    page_number = 1
    while True:
        cut = text[2000 * (page_number - 1):2000 * page_number]
        if len(cut) == 0:
            break
        else:
            await ctx.reply(f"```{cut}```")
        page_number += 1


@bot.command(name=main_config['short_server_name'] + "_get_claim")
async def get_claim(ctx, user_name: str = None):
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
            if role.__str__() == replies['master_role']:
                cur_user = user_name
    if cur_user in wipes.last_wipe.claims:
        text = json.dumps(wipes.last_wipe.claims[cur_user], default=lambda o: o.__dict__, ensure_ascii=False, indent=4)
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
        await ctx.reply(replies["get_claim_fail"])
        return False


@bot.event
async def on_message(ctx):
    if ctx.author != bot.user:
        if len(ctx.content) > 0:
            if ctx.content[0] == main_config['prefix']:
                if ctx.channel.id in replies['commands_channel_id']:
                    await bot.process_commands(ctx)
            else:
                if wipes.last_wipe.stoped_at == "":
                    if message := re.findall(
                            r'''Сервер: ''' + main_config['server_name'] + '''[\s]*?Игровой ник: ([\w\d]+?)[\s]*?Прошу:[\s]*?([\w\W]+)''',
                            ctx.content):
                        loot = re.findall(r'''(\w[\w\s].+?) \("([\w].+?)"\)''', message[0][1])
                        print(f"Игровой ник: {message[0][0]}")
                        for item in loot:
                            print(f"Игровое название предмета: {item[0]}")
                            print(f"Код для консоли: {item[1]}")

                        wipes.last_wipe.claims[ctx.author.__str__()] = Claim(
                            Player(ctx.author.__str__(), message[0][0]),
                            tuple(Item(item[0], item[1]) for item in loot),
                            ctx.created_at.__str__(),
                            wipes.last_wipe.path,
                        )
                        wipes.last_wipe.claims[ctx.author.__str__()].save()
                        await ctx.add_reaction(replies['claim_accepted_is_ok'])


bot.run(main_config['token'])
