import subprocess

from chesterbot import main_config


async def restart():
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

async def soft_restart():
    """Перезапускает сервер через 1 минуту"""
    try:
        print(
            subprocess.check_output(
                f"""screen -dmS "soft_restarting_server" {main_config['short_server_name']}_soft_restart.sh""",
                shell=True
            )
        )
        return True
    finally:
        return False

async def soft_stop():
    """Останавливает сервер через 1 минуту"""
    try:
        print(
            subprocess.check_output(
                f"""screen -dmS "soft_stop_server" {main_config['short_server_name']}_soft_stop.sh""",
                shell=True
            )
        )
        return True
    finally:
        return False

async def start():
    """Запускает сервер"""
    try:
        print(
            subprocess.check_output(
                f"""{main_config['short_server_name']}_start.sh""",
                shell=True
            )
        )
        return True
    finally:
        return False

async def stop():
    """Останавливает сервер сразу"""
    try:
        print(
            subprocess.check_output(
                f"""{main_config['short_server_name']}_stop.sh""",
                shell=True
            )
        )
        return True
    finally:
        return False