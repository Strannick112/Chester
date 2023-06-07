helps = {
    "@admin": {
        "short_info": "Упоминание админа в дискорде",
        "extended_info":
            "Если вставить @admin в текст сообщения (не шёпота!) в игровом чате,"
            " то @admin заменится на упоминание роли администратора на дискорд сервере"
    },
    "@give_items": {
        "short_info": "Выдает предметы",
        "extended_info":
            "При наличии одобренной администраторами заявки в дискорд сервере можно получить предметы в игре."
            " Достаточно написать в чат @give_items"
    },
    "где база?": {
        "short_info": "Гайд о том, как найти базу",
        "extended_info":
            "Никак. На сервере установлен мод на приваты. "
            "Это позволяет, с одной стороны, сохранять игрокам добытые ресурсы нетронутыми, "
            "с другой стороны, позволяет игрокам, присоединившимся в разное время, прогрессировать независимо. "
            "P.S.: Иногда добрые игроки делают мини-базу для новичков либо на спавне, либо у короля свиней."
    },
    "синхронизатор чата": {
        "short_info": "Данные о работе синхронизатора чата",
        "extended_info":
            "Общее правило: сообщения из игрового чата отправляются в наш дискорд сервер. "
            "Сообщения из нашего дискорд сервера отправляются в игровой чат. "
            "Таким образом, люди, находящиеся в игре, могут общаться с людьми, которые сидят в дискорде. "
    },
    "особенности синхронизатора": {
        "short_info": "Перечисление особенностей работы синхронизатора чата",
        "extended_info":
            "Синхронизатор чата не отправляет на дискорд сервер сообщения, которые начинаются с символа '$'. "
            "Синхронизатор чата не отправляет на дискорд сервер игровой шёпот. "
            "Игровой шёпот могут видеть администраторы игрового сервера."
    },
}

short_command_list = ", ".join(tuple(command for command in helps))
extended_command_list = "\n".join(tuple(key + ": " + value["short_info"] for key, value in helps.items()))
