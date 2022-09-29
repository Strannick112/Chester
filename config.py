
config = {
    'token': 'token',
    'prefix': '$',
    'server_name': "Server_Name",
    'short_server_name': "SN",
    'server_main_screen_name': 'Server_Main_Screen_Name',
}

replies = {
    "start_success": "Успешный старт",
    "start_fail": "Не успешный старт",
    "stop_success": "Успешная остановка",
    "stop_fail": "Не успешная остановка",
    "give_items_success": "Успешная выдача предметов",
    "give_items_fail": "Не успешная выдача предметов",
    "give_items_fail_who_are_you": "Я тебя не знаю",
    "give_items_fail_not_approved": "Заявка не подтверждена",
    "give_items_fail_executed": "Перенос вещей по заявке уже выполнен",
    "change_replies_success": "Смена фразы произведена успешно",
    "change_replies_fail": "Смена фразы не удалась",
    "text_is_too_big_to_send": "Текст слишком велик для отправки, поэтому он будет передан в виде файла",
    "get_claim_fail": "Заявка не найдена",

    'master_role': 'Master_Role',
    'claim_accepted_is_ok': 'reaction',
    'claim_admin_approved_is_ok': 'reaction',
    'claim_error': 'reaction',
    'claim_items_executed': 'reaction',
    'claim_is_overdue': 'reaction',
    'claim_full_approved': 'reaction',
    'claim_channel_id': 123123123,
    'commands_channel_id': 123123123,
}

# for locally rewrite settings add it to settings_local.py
try:
    from config_local import *
except ModuleNotFoundError as err:
    pass
