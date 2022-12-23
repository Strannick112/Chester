import datetime

from discord.ext import commands

from chester_bot import wipes, bot, replies, main_config
from chester_bot.wipes.Status import Status


@bot.command(name=main_config['short_server_name'] + "_checkout_marks_on_executed_claims")
@commands.has_role(replies['master_role'])
async def checkout_marks_on_executed_claims(ctx):
    "Синхронизирует реакции под всеми сообщениями с заявками, хранящимися у бота"
    for user_name, claim in wipes.last_wipe.claims.items():
        for channel_id in replies['claim_channel_id']:
            async for msg in bot \
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
                            if reaction.__str__() == replies['claim_accepted_is_ok']:
                                has_reactions['claim_accepted_is_ok'] = True
                            if reaction.__str__() == replies['claim_full_approved']:
                                has_reactions['claim_items_executed'] = True
                            if reaction.__str__() == replies['claim_items_executed']:
                                has_reactions['claim_items_executed'] = True

                    if not has_reactions['claim_accepted_is_ok']:
                        await msg.add_reaction(replies['claim_accepted_is_ok'])

                    if has_reactions['claim_full_approved']:
                        if claim.status not in (Status.approved, Status.executed):
                            msg.remove_reaction(replies['claim_full_approved'], bot.user)
                    else:
                        if claim.status in (Status.approved, Status.executed):
                            await msg.add_reaction(replies['claim_full_approved'])

                    if has_reactions['claim_items_executed']:
                        if claim.status != Status.executed:
                            await msg.remove_reaction(replies['claim_items_executed'], bot.user)
                    else:
                        if claim.status == Status.executed:
                            await msg.add_reaction(replies['claim_items_executed'])

    await ctx.reply(replies['checkout_marks_on_executed_claims_success'])
    return True