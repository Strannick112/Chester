from datetime import datetime

from chester_bot import wipes, bot, replies
from chester_bot.bot_commands.utils.make_claim import make_claim
from chester_bot.config import main_config


@bot.command(name=main_config['short_server_name'] + "_delete_claim")
async def delete_claim(ctx, user_name: str = None):
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
            if role.__str__() == replies['master_role']:
                cur_user = user_name
    if cur_user in wipes.last_wipe.claims:
        for channel_id in replies['claim_channel_id']:
            async for msg in bot \
                    .get_channel(channel_id) \
                    .history(
                after=datetime.strptime(wipes.last_wipe.started_at, '%Y-%m-%d %H:%M:%S.%f%z')
            ):
                if msg.author == bot.user:
                    continue
                if msg.author == cur_user:
                    if (claim := make_claim(msg.content, msg.author, msg.created_at)) is not None \
                            and claim.equal(wipes.last_wipe.claims[cur_user]):
                        await msg.add_reaction()
        wipes.last_wipe.claims[cur_user].delete()
        del wipes.last_wipe.claims[cur_user]
        await ctx.reply(replies['delete_claim_success'])
        return True
    else:
        await ctx.reply(replies["delete_claim_fail"])
        return False
