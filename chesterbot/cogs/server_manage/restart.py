import subprocess

from chesterbot import main_config


async def restart(*args, **kwargs):
    try:
        print(
            subprocess.check_output(
                f"""screen -dmS "restart_server" {main_config['short_server_name']}_restart.sh""",
                shell=True
            )
        )
        return True
    finally:
        return False
