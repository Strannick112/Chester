# import datetime
#
# from discord.ext import commands
#
# from chester_bot import wipes, bot, replies, main_config
#
#
# @commands.command(name=main_config['short_server_name'] + "_rollback_claims")
# @commands.has_role(replies['master_role'])
# async def rollback_claims(ctx):
#     """Изменяет у всех заявок статус "Выполнена" на "Одобрена", таким образом, позволяя взять вещи еще раз."""
#     for user_name, claim in wipes.last_wipe.claims.items():
#         if claim.rollback_claim():
#             for channel_id in replies['claim_channel_id']:
#                 async for msg in bot.get_channel(channel_id).history(
#                     after=datetime.datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
#                 ):
#                     if msg.author.__str__() == user_name:
#                         for reaction in msg.reactions:
#                             if reaction.__str__() == replies['claim_items_executed']:
#                                 if reaction.me:
#                                     await msg.remove_reaction(replies['claim_items_executed'], bot.user)
#     await ctx.reply(replies['rollback_claims_success'])
#     return True
