import datetime

from discord.ext import commands

from chester_bot import wipes, bot, replies
from chester_bot.wipes.Wipe import Wipe
from chester_bot.config import main_config


@bot.command(name=main_config['short_server_name'] + "_start_wipe")
@commands.has_role(replies['master_role'])
async def start_wipe(ctx):
    """Открывает приём заявок от игроков"""
    if wipes.last_wipe.started_at == "" or wipes.last_wipe.stoped_at != "" or wipes.last_wipe.path == "./wipes/_":
        wipes.last_wipe = Wipe(
            claims={},
            server_name=main_config['server_name'],
            started_at=ctx.message.created_at.__str__(),
        )
        wipes.last_wipe.save()
        for channel_id in replies['claim_channel_id']:
            async for msg in bot \
                    .get_channel(channel_id) \
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
