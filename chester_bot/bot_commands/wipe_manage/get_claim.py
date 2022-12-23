import json

from chester_bot import wipes, bot, replies
from chester_bot.config import main_config


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
