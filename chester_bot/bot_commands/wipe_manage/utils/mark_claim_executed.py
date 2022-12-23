import datetime

from chester_bot import wipes, bot, replies


async def mark_claim_executed(user_name: str):
    for channel_id in replies['claim_channel_id']:
        async for msg in bot \
                .get_channel(channel_id) \
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