import datetime

from discord.ext import commands

from chester_bot import wipes, bot, replies
from chester_bot.config import main_config


@bot.command(name=main_config['short_server_name'] + "_stop_wipe")
@commands.has_role(replies['master_role'])
async def stop_wipe(ctx):
    """Закрывает набор заявок от игроков"""
    if wipes.last_wipe.stoped_at == "":
        await ctx.reply(replies['stop_success'])
        cur_time = ctx.message.created_at.__str__()
        wipes.last_wipe.stoped_at = cur_time
        wipes.last_wipe.save()
        for channel_id in replies['claim_channel_id']:
            async for msg in bot \
                    .get_channel(channel_id) \
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
