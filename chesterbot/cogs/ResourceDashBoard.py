import asyncio
import copy

import discord


class ResourceDashBoard:
    def __init__(self, bot, world):
        self.chester_bot = bot
        self.shard_id = world["shard_id"]
        self.public_name = world["public_name"]
        self.screen_name = world["screen_name"]
        self.data = copy.deepcopy(ResourceDashBoard.__data[world["world_type"]])

    __overworld = {
        "Боссы": {
            "Дружелюбная фруктовая муха": {"friendlyfruitfly": 0},
            "Драконья муха": {"dragonfly": 0},
            "Гломмер": {"glommer": 0},
            "Мешок клауса": {"klaus_sack": 0},
            "Улей пчелиной королевы": {"beequeenhivegrown": 0},
            "Медведь-барсук": {"bearger": 0},
            "Циклоп-олень": {"deerclops": 0},
            "Яйца Гусь-лусей": {"mooseegg": 0},
            "Гусь-лусь": {"moose": 0},
            "Лусята": {"mossling": 0},
            "Муравьиный лев": {"antlion": 0},
            "Король-краб": {"crabking": 0},
            "Скелеты игроков": {"skeleton": 0},
            "Одержимый варг": {"mutatedwarg": 0},
            "Кристальный циклоп-олень": {"mutateddeerclops": 0},
            "Бронированный медведь-барсук": {"mutatedbearger": 0}
        },
        "Существа": {
            "Вольт-козы": {"lightninggoat": 0},
            "Бифало": {"beefalo": 0},
            "Хижины моржей": {"walrus_camp": 0},
            "Моржи": {"walrus": 0},
            "Дома свиней": {"pighouse": 0},
            "Дома мермов": {"mermhouse": 0},
            "Мермы": {"merm": 0},
            "Щупальца": {"tentacle": 0},
            "Шахматы": {"knight": 0, "bishop": 0, "rook": 0},
            "Енотокоты": {"catcoon": 0},
            "Дикие улья": {"beehive": 0},
            "Улья пчёл-убийц": {"wasphive": 0},
            "Смертоносные светлоцветы": {"lunarthrall_plant": 0},
            "Логова выдр": {"otterden": 0}
        },
        "Ресурсы": {
            "Кусты камыша": {"reeds": 0},
            "Кусты каменных фруктов": {"rock_avocado_bush": 0},
            "Перекати-поле": {"tumbleweed": 0},
            "Спаунеры перекати-поле": {"tumbleweedspawner": 0},
            "Приманкоцветы": {"lureplant": 0},
            "Разломы": {"lunarrift_portal": 0},
            "Кристаллы разлома": {"lunarrift_crystal_big": 0},
            "Подводный объект": {"underwater_salvageable": 0}
        }
    }

    __caves = {
        "Боссы": {
            "Древний страж": {"minotaur": 0},
            "Дружелюбная фруктовая муха": {"friendlyfruitfly": 0},
            "Кошмарный свин-оборотень": {"daywalker": 0},
            "Скелеты игроков": {"skeleton": 0}
        },
        "Существа": {
            "Проглоты": {"slurper": 0},
            "Глубинные черви": {"worm": 0},
            "Лобстеры": {"rocky": 0},
            "Дома зайцев": {"rabbithouse": 0},
            "Логова мотыльков": {"dustmothden": 0},
            "Обезьяньи тотемы": {"monkeybarrel": 0},
            "Щупальца": {"tentacle": 0},
            "Повреждённых шахмат на охране руин": {
                "knight_nightmare": 0,
                "bishop_nightmare": 0,
                "rook_nightmare": 0,
            },
            "Спилагмиты": {"spiderhole": 0}
        },
        "Ресурсы": {
            "Статуи в руинах": {
                "ruins_statue_mage": 0,
                "ruins_statue_mage_nogem": 0,
                "ruins_statue_head": 0,
                "ruins_statue_head_nogem": 0
            },
            "Кусты камыша": {"reeds": 0},
            "Сундуки в лабиринте": {"pandoraschest": 0},
            "Теневой разлом": {"shadowrift_portal": 0},
            "Сталагмиты": {
                "stalagmite_full": 0,
                "stalagmite_med": 0,
                "stalagmite_low": 0,
                "stalagmite_tall_full": 0,
                "stalagmite_tall_med": 0,
                "stalagmite_tall_low": 0
            }
        }
    }

    __build = {
        "Боссы": {
            "Дружелюбная фруктовая муха": {"friendlyfruitfly": 0},
            "Скелеты игроков": {"skeleton": 0}
        },
        "Существа": {
            "Бифало": {"beefalo": 0},
            "Дома свиней": {"pighouse": 0},
            "Дома мермов": {
                "mermhouse_crafted": 0,
                "mermwatchtower": 0
            },
            "Дома зайцев": {"rabbithouse": 0},
            "Паучьи коконы": {
                "spiderden": 0,
                "spiderden_2": 0,
                "spiderden_3": 0
            },
            "Пасеки": {"beebox": 0},
            "Мермы": {"merm": 0},
            "Щупальца": {"tentacle": 0}
        },
        "Ресурсы": {
            "Кусты каменных фруктов": {"rock_avocado_bush": 0},
            "Приманкоцветы": {"lureplant": 0},
            "Обезьяньи хвостики": {"monkeytail": 0},
            "Ягодные кусты": {
                "berrybush": 0,
                "berrybush2": 0,
                "berrybush_juicy": 0
            }
        }
    }

    __data = {
        "overworld": __overworld,
        "caves": __caves,
        "build": __build
    }

    async def make_dashboard(self):
        embed = discord.Embed(color=0x2F3136, title=self.public_name)
        for group_name, group in self.data.items():
            text = ""
            for prefab_name, prefab_info in group.items():
                text += prefab_name + ": " + (sum(prefab_info.values()).__str__()) + "\n"
            embed.add_field(name="", value=f"**{group_name}**\n{text}", inline=True)
        return embed

    async def reload_data(self):
        for group_name, group in self.data.items():
            for prefab_name, prefab_info in group.items():
                for prefab_code, prefab_count in prefab_info.items():
                    command = f"local count = 0 local prefab = \\\"{prefab_code}\\\" " \
                              "for k,v in pairs(Ents) do if v.prefab == prefab then " \
                              "count = count + 1 end end print(\\\"CountPrefab\\\", prefab, count)"
                    self.data[group_name][prefab_name][prefab_code] = int(
                        await asyncio.create_task(
                            self.chester_bot.console_dst_checker.check_selected_world(
                                command, r"CountPrefab\s*" + prefab_code + r"\s*([\d]+)\s*",
                                self.shard_id, self.screen_name, prefab_count, 30
                            )
                        )
                    )
