import codecs
import os
import select
import subprocess

main_config = {
    'token': 'token',
    'prefix': '$',
    'server_name': 'Server_Name',
    'short_server_name': 'SN',
    'server_main_screen_name': 'Server_Main_Screen_Name',
    'master_role': 0,
    'default_role_id': 'Default_Role_id',

    "game_chat_sync_channel": 0,
    "game_log_sync_channel": 0,
    "command_channel": 0,
    "dashboard_channel": 0,
    "description": "short description of the server",
    "path_to_save": "/path/to/save_folder",
    "main_embed_picture": "url_to_image",

    "is_event": False,

    "buttons": [
        {"description": "description by default", "url": "https://discord.gg/NFGxUDDbz7"}
    ],

    "worlds": [
        {"public_name": "Обычный мир, поверхность", "shard_id": "1", "world_type": "overworld", "folder_name": "Shard 1"},
        {"public_name": "Обычный мир, пещеры", "shard_id": "2", "world_type": "caves", "folder_name": "Shard 2"},
        {"public_name": "Изменённый мир, поверхность", "shard_id": "3", "world_type": "overworld", "folder_name": "Shard 3"},
    ],

    'sql_connection_row': "postgresql+asyncpg://admin:admin@localhost/dst_keriwell",
    'connect_args': {'ssl': 'disable'}
}


# for locally rewrite settings add it to settings_local.py
try:
    from chesterbot.config_local import *
except ModuleNotFoundError as err:
    pass


for world in main_config["worlds"]:
    world["full_path_to_server_log_file"] = main_config['path_to_save'] + "/" + world["folder_name"] + "/server_log.txt"
    world["file_log_size"] = os.path.getsize(world["full_path_to_server_log_file"])
    world["file_log_iter"] = codecs.open(
        world["full_path_to_server_log_file"], "r", encoding="utf-8", errors='ignore'
    )
    world["file_log_iter"].seek(0, 2)
    world["screen_name"] = main_config['short_server_name'] + world["shard_id"]

main_config["full_path_to_server_chat_log_file"] = \
    main_config['path_to_save'] + "/" + main_config["worlds"][0]["folder_name"] + "/server_chat_log.txt"
main_config["file_chat_size"] = os.path.getsize(main_config["full_path_to_server_chat_log_file"])
main_config["file_chat_iter"] = codecs.open(
    main_config["full_path_to_server_chat_log_file"], "r", encoding="utf-8", errors='ignore'
)
main_config["file_chat_iter"].seek(0, 2)

