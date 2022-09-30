
main_config = {
    'token': 'token',
    'prefix': '$',
    'server_name': 'Server_Name',
    'short_server_name': 'SN',
    'server_main_screen_name': 'Server_Main_Screen_Name',
}


# for locally rewrite settings add it to settings_local.py
try:
    from config_local import *
except ModuleNotFoundError as err:
    pass
