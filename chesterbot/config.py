main_config = {
    'token': 'token',
    'prefix': '$',
    'server_name': 'Server_Name',
    'short_server_name': 'SN',
    'server_main_screen_name': 'Server_Main_Screen_Name',
    'master_role': 'Master_Role',

    "game_chat_sync_channel": 0,
    "game_log_sync_channel": 0,
    "path_to_log": "/path/to/log/file"
}


# for locally rewrite settings add it to settings_local.py
try:
    from chesterbot.config_local import *
except ModuleNotFoundError as err:
    pass
