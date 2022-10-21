from chester_bot import bot, replies, wipes
from chester_bot.bot_commands.utils.make_claim import make_claim
from chester_bot.config import main_config


@bot.event
async def on_message(ctx):
    if ctx.author != bot.user:
        if len(ctx.content) > 0:
            if ctx.content[0] == main_config['prefix']:
                if ctx.channel.id in replies['commands_channel_id']:
                    await bot.process_commands(ctx)
            else:
                if wipes.last_wipe.stoped_at == "":
                    author = ctx.author.__str__()
                    claim = make_claim(ctx.content, author, ctx.created_at.__str__())
                    if claim is not None:
                        wipes.last_wipe.claims[author] = claim
                        wipes.last_wipe.claims[author].save()
                        await ctx.add_reaction(replies['claim_accepted_is_ok'])
