import codecs
import select
import subprocess

main_config = {
    'token': 'token',
    'prefix': '$',
    'server_name': 'Server_Name',
    'short_server_name': 'SN',
    'server_main_screen_name': 'Server_Main_Screen_Name',
    'master_role': 'Master_Role',
    'default_role_id': 'Default_Role_id',

    "game_chat_sync_channel": 0,
    "game_log_sync_channel": 0,
    "path_to_save": "/path/to/save_folder",

    "worlds": [
        {"public_name": "Обычный мир, поверхность", "shard_id": "1", "world_type": "overworld", "folder_name": "Shard 1"},
        {"public_name": "Обычный мир, пещеры", "shard_id": "2", "world_type": "caves", "folder_name": "Shard 2"},
        {"public_name": "Изменённый мир, поверхность", "shard_id": "3", "world_type": "overworld", "folder_name": "Shard 3"},
    ]
}


# for locally rewrite settings add it to settings_local.py
try:
    from chesterbot.config_local import *
except ModuleNotFoundError as err:
    pass


for world in main_config["worlds"]:
    world["file_log_iter"] = codecs.open(
        main_config['path_to_save'] + "/" + world["folder_name"] + "/server_log.txt", "r"
    )
    world["file_log_iter"].seek(0, 2)
    world["file_chat_iter"] = codecs.open(
        main_config['path_to_save'] + "/" + world["folder_name"] + "/server_chat_log.txt", "r"
    )
    world["file_chat_iter"].seek(0, 2)