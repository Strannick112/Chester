import subprocess
from chester_bot import bot, replies
from chester_bot.config import main_config


@bot.command(name=main_config['short_server_name'] + "_stop_server")
async def stop_server(ctx):
    """Останавливает сервер сразу"""
    for role in ctx.author.roles:
        if role.__str__() == replies['master_role']:
            print(
                subprocess.check_output(
                    f"""{main_config['short_server_name']}_stop.sh""",
                    shell=True
                )
            )
            return True
    return False
