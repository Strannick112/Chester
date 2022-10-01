from chester_bot import wipes, bot, replies
from chester_bot.wipes.Status import Status
from chester_bot.config import main_config
from chester_bot.bot_commands.utils.mark_claim_executed import mark_claim_executed


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
