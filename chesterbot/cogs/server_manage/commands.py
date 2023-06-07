import re
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


async def soft_world_regenerate():
    """Останавливает сервер сразу"""
    try:
        subprocess.check_output(
            f"""screen -S {main_config['server_main_screen_name']} -X stuff""" +
            f""" "c_regenerateworld()\n\"""",
            shell=True
        )
        return True
    finally:
        return False


async def send_message_to_game(author: str, text: str):
    """Отправляет сообщение от указанного автора в игру"""
    try:
        screen_list = subprocess.run(
            'screen -ls',
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        ).stdout.decode('ascii')
        if main_config['server_main_screen_name'] in screen_list:
            nickname = re.sub(r'\'', r"\\\\\'", author)
            nickname = re.sub(r'\"', r"\\\\\"", nickname)
            nickname = re.sub(r'\$', r"\\\\\$", nickname)
            nickname = re.sub(r'>', r"\\\\\>", nickname)
            nickname = re.sub(r'<', r"\\\\\<", nickname)
            nickname = re.sub(r'/', r"\\\\\/", nickname)
            text = re.sub(r'\'', r"\\\\\'", text)
            text = re.sub(r'\"', r"\\\\\"", text)
            text = re.sub(r'\$', r"\\\\\$", text)
            text = re.sub(r'>', r"\\\\\>", text)
            text = re.sub(r'<', r"\\\\\<", text)
            text = re.sub(r'/', r"\\\\\/", text)
            subprocess.check_output(
                f"""screen -S {main_config['server_main_screen_name']} -X stuff""" +
                f""" "c_announce(\\\"{nickname}: {text}\\\")\n\"""",
                shell=True
            )
        return True
    finally:
        return False


