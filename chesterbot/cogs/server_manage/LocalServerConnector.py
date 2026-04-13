import re
import subprocess

from chesterbot import main_config

class LocalServerConnector:

    def __init__(self):
        pass

    async def restart_server(self):
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

    async def soft_restart_server(self):
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

    async def soft_stop_server(self):
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

    async def start_server(self):
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

    async def stop_server(self):
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

    async def soft_world_regenerate(self):
        """Перегенерирует сервер спустя минуту"""
        try:
            subprocess.check_output(
                f"""screen -S {main_config['server_main_screen_name']} -X stuff""" +
                f""" "c_regenerateworld()\n\"""",
                shell=True
            )
            return True
        finally:
            return False

    async def send_message_to_game(self, author: str, text: str):
        """Отправляет сообщение от указанного автора в игру"""
        try:
            screen_list = subprocess.run(
                'screen -ls',
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE
            ).stdout.decode('ascii')
            if main_config['server_main_screen_name'] in screen_list:
                nickname = await self.__normalize_text(author)
                text = await self.__normalize_text(text)
                subprocess.check_output(
                    f"""screen -S {main_config['server_main_screen_name']} -X stuff""" +
                    f""" "c_announce(\\\"{nickname}: {text}\\\")\n\"""",
                    shell=True
                )
            return True
        finally:
            return False

    async def __normalize_text(self, text):
        text = re.sub(r'\'', r"\\\\\'", text)
        text = re.sub(r'\"', r"\\\\\"", text)
        text = re.sub(r'\$', r"\\\\\$", text)
        text = re.sub(r'>', r"\\\\\>", text)
        text = re.sub(r'<', r"\\\\\<", text)
        text = re.sub(r'/', r"\\\\\/", text)
        return text

    async def __command_execute(self, command ="", shard_id = main_config["worlds"][0]["shard_id"]):
        command_line = re.sub(r'\"', r"\"", re.sub(r'\'', r"\'", command))
        subprocess.check_output(
            f"""screen -S {main_config['short_server_name']}{shard_id} -X stuff""" +
            f""" "{command_line}\n\"""",
            shell=True
        )
        return command_line

    async def command(self, command, shard_id = main_config["worlds"][0]["shard_id"]):
        return await self.__command_execute(command, shard_id)

    async def ban(self, ku_id):
        return await self.__command_execute(f"TheNet:Ban(\"{ku_id}\")")

# async def send_announce_to_game(text: str, color: tuple = (255, 0, 0, 1)):
#     """Отправляет сообщение от указанного автора в игру"""
#     try:
#         screen_list = subprocess.run(
#             'screen -ls',
#             shell=True,
#             stdout=subprocess.PIPE,
#             stdin=subprocess.PIPE
#         ).stdout.decode('ascii')
#         if main_config['server_main_screen_name'] in screen_list:
#             nickname = re.sub(r'\'', r"\\\\\'", author)
#             nickname = re.sub(r'\"', r"\\\\\"", nickname)
#             nickname = re.sub(r'\$', r"\\\\\$", nickname)
#             nickname = re.sub(r'>', r"\\\\\>", nickname)
#             nickname = re.sub(r'<', r"\\\\\<", nickname)
#             nickname = re.sub(r'/', r"\\\\\/", nickname)
#             text = re.sub(r'\'', r"\\\\\'", text)
#             text = re.sub(r'\"', r"\\\\\"", text)
#             text = re.sub(r'\$', r"\\\\\$", text)
#             text = re.sub(r'>', r"\\\\\>", text)
#             text = re.sub(r'<', r"\\\\\<", text)
#             text = re.sub(r'/', r"\\\\\/", text)
#             subprocess.check_output(
#                 f"""screen -S {main_config['server_main_screen_name']} -X stuff""" +
#                 f""" "Networking_Announcement(\\\"{text}\\\", """ + """{""" +
#                 f"""{color[0]}, {color[1]}, {color[2]}, {color[3]}""" + """}, \\\"mod\\\")\n\"""",
#                 shell=True
#             )
#         return True
#     finally:
#         return False
