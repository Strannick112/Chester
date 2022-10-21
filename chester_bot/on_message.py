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
                    # if message := re.findall(
                    #         r'''Сервер: ''' + main_config['server_name'] + '''[\s]*?Игровой ник: ([\w\d]+?)[\s]*?Прошу:[\s]*?([\w\W]+)''',
                    #         ctx.content):
                    #     loot = re.findall(r'''(\w[\w\s].+?) \("([\w].+?)"\)''', message[0][1])
                    #     print(f"Игровой ник: {message[0][0]}")
                    #     for item in loot:
                    #         print(f"Игровое название предмета: {item[0]}")
                    #         print(f"Код для консоли: {item[1]}")

                        # wipes.last_wipe.claims[ctx.author.__str__()] = Claim(
                        #     Player(ctx.author.__str__(), message[0][0]),
                        #     tuple(Item(item[0], item[1]) for item in loot),
                        #     ctx.created_at.__str__(),
                        #     wipes.last_wipe.path,
                        # )
                    author = ctx.author.__str__()
                    claim = make_claim(ctx.content, author, ctx.created_at.__str__())
                    if claim is not None:
                        wipes.last_wipe.claims[author] = claim
                        wipes.last_wipe.claims[author].save()
                        await ctx.add_reaction(replies['claim_accepted_is_ok'])
