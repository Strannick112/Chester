import subprocess
from chester_bot import bot, replies
from chester_bot.config import main_config


@bot.command(name=main_config['short_server_name'] + "_soft_restart_server")
async def soft_restart_server(ctx):
    """Перезапускает сервер через 1 минуту"""
    for role in ctx.author.roles:
        if role.__str__() == replies['master_role']:
            print(
                subprocess.check_output(
                    f"""screen -dmS "soft_restarting_server" {main_config['short_server_name']}_soft_restart.sh""",
                    shell=True
                )
            )
            return True
    return False
