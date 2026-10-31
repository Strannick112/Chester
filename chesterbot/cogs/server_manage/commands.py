import re
import subprocess
import configparser
import base64
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


async def send_message_to_game(author: str, text: str) -> bool:
    """Отправляет сообщение в DST, передавая текст в виде чисел.
    Полностью защищает от Lua-инъекций и не вызывает лагов игры.
    """
    try:
        # 1. Проверяем наличие экрана БЕЗ shell=True
        result = subprocess.run(
            ['screen', '-ls'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if main_config['server_main_screen_name'] not in result.stdout:
            return False

        # Полная строка сообщения, которую должен увидеть сервер
        full_message = f"{author}: {text}"

        # 2. Переводим каждый символ строки в его числовой ID (ASCII/UTF-8 байт)
        # Пример: "A" станет 65, "B" станет 66. Хакерский код станет просто набором цифр.
        byte_list = [str(b) for b in full_message.encode('utf-8')]
        bytes_string = ", ".join(byte_list)  # Получится строка вида: "72, 97, 99, 107, 101, 114"

        # 3. Формируем команду для DST.
        # string.char(72, 97, ...) мгновенно собирает строку в памяти Lua на Си-уровне.
        # Никаких циклов, никаких кавычек, в которые можно внедриться!
        lua_command = f"c_announce(string.char({bytes_string}))\n"

        # 4. Отправляем в screen БЕЗ shell=True
        subprocess.run([
            'screen',
            '-S', main_config['server_main_screen_name'],
            '-X', 'stuff',
            lua_command
        ], check=True)

        return True
    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        return False

async def turn_on_pvp():
    config, file_path = pvp_config()
    config.set("GAMEPLAY", "pvp", "true")
    with open(file_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)
    await soft_restart()

async def turn_off_pvp():
    config, file_path = pvp_config()
    config.set("GAMEPLAY", "pvp", "false")
    with open(file_path, "w", encoding="utf-8") as configfile:
        config.write(configfile)
    await soft_restart()

def pvp_config():
    file_path = main_config["path_to_save"] + "/cluster.ini"
    config = configparser.ConfigParser()
    config.optionxform = str
    config.read(file_path, encoding="utf-8")
    return config, file_path

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