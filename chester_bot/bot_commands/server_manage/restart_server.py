import subprocess
from chester_bot import bot, replies
from chester_bot.config import main_config


@bot.command(name=main_config['short_server_name'] + "_restart_server")
async def restart_server(ctx):
    """Перезапускает сервер сразу"""
    for role in ctx.author.roles:
        if role.__str__() == replies['master_role']:
            print(
                subprocess.check_output(
                    f"""screen -dmS "restart_server" {main_config['short_server_name']}_restart.sh""",
                    shell=True
                )
            )
            return True
    return False
