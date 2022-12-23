import subprocess
from chester_bot import bot, replies
from chester_bot.config import main_config


@bot.command(name=main_config['short_server_name'] + "_soft_stop_server")
async def soft_stop_server(ctx):
    """Выдает игроку предметы на сервере по оставленной и подтверждённой заявке"""
    for role in ctx.author.roles:
        if role.__str__() == replies['master_role']:
            print(
                subprocess.check_output(
                    f"""{main_config['short_server_name']}_soft_stop.sh""",
                    shell=True
                )
            )
            return True
    return False
