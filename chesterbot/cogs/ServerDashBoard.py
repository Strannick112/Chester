import asyncio
import discord

from chesterbot import main_config


class ServerDashBoard:
    def __init__(self, bot, world):
        self.chester_bot = bot
        self.shard_id = world["shard_id"]
        self.public_name = world["public_name"]
        self.screen_name = world["screen_name"]
        self.data = ServerDashBoard.__data[world["world_type"]].copy()

    __data = {
        "overworld": {
            "Характеристики сервера": {
                "Сезон": {"season": "Осень"},
                "Время суток": {"day_time": "День"},
            }
        }
    }

    async def _get_season(self):
        return await self.chester_bot.console_dst_checker.check(
            f"screen -S {self.screen_name} -X stuff \"print(\\\"Season\\\", TheWorld.components.worldstate.data.season)\n\"",
            r"Season\s*([\w]+)\s*", self.shard_id, self.screen_name, "unknown", 5
        )

    async def _get_cycles(self):
        return await self.chester_bot.console_dst_checker.check(
            f"screen -S {self.screen_name} -X stuff \"print(\\\"Cycles\\\", TheWorld.components.worldstate.data.cycles)\n\"",
            r"Cycles\s*([\d]+)\s*", self.shard_id, self.screen_name, 0, 5
        )

    async def make_dashboard(self):
        embed = discord.Embed(colour=discord.Colour.dark_teal())
        embed.set_author(name=main_config["server_name"])
        embed.add_field(name="", value=main_config["description"], inline=False)
        embed.add_field(name="", value="День: " + (await self._get_cycles()).__str__())
        # embed.add_field(name="", value="Сезон: " + self.chester_bot.replies["autumn_emoji"], inline=True)
        embed.add_field(name="", value="Сезон: " + self.chester_bot.replies[await self._get_season()], inline=True)
        # for group_name, group in self.data.items():
        #     text = ""
        #     for prefab_name, prefab_info in group.items():
        #         text += prefab_name + ": " + list(prefab_info.values())[0] + ";\n"
        #     embed.add_field(name=group_name, value=text, inline=False)
        return embed

    async def reload_data(self):
        pass
        # for group_name, group in self.data.items():
        #     for prefab_name, prefab_info in group.items():
        #         for prefab_code, prefab_count in prefab_info.items():
        #             command = f"screen -S {self.screen_name} -X stuff "\
        #                              f"\"local count = 0 local prefab = \\\"{prefab_code}\\\" "\
        #                              "for k,v in pairs(Ents) do if v.prefab == prefab then "\
        #                              "count = count + 1 end end print(\\\"CountPrefab\\\", prefab, count)\n\""
        #             self.data[group_name][prefab_name][prefab_code] = int(
        #                 await asyncio.create_task(
        #                     self.chester_bot.console_dst_checker.check(
        #                         command, r"CountPrefab\s*" + prefab_code + r"\s*([\d]+)\s*",
        #                         self.shard_id, self.screen_name, prefab_count, 30
        #                     )
        #                 )
        #             )
