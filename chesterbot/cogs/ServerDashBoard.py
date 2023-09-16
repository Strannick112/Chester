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
            r"Season\s*([\w]+)\s*", self.shard_id, self.screen_name, "unknown_emoji", 5
        )

    async def _get_cycles(self):
        return await self.chester_bot.console_dst_checker.check(
            f"screen -S {self.screen_name} -X stuff \"print(\\\"Cycles\\\", TheWorld.components.worldstate.data.cycles)\n\"",
            r"Cycles\s*([\d]+)\s*", self.shard_id, self.screen_name, 0, 5
        )

    async def _get_day_phase(self):
        return await self.chester_bot.console_dst_checker.check(
            f"screen -S {self.screen_name} -X stuff \"print(\\\"Day phase\\\", TheWorld.components.worldstate.data.phase)\n\"",
            r"Day phase\s*([\w]+)\s*", self.shard_id, self.screen_name, "unknown_emoji", 5
        )

    async def make_dashboard(self):
        embed = discord.Embed(color=0x2F3136)
        # embed.set_thumbnail(url="https://media.discordapp.net/attachments/972971947224870932/1152296441000251472/images.png")
        embed.set_author(name=main_config["server_name"])
        description = main_config["description"]
        description += "ᅠ День: " + (await self._get_cycles()).__str__()
        description += "ᅠ Сезон: " + self.chester_bot.replies[await self._get_season()]
        description += "ᅠ Время суток: " + self.chester_bot.replies[await self._get_day_phase()]
        # embed.add_field(name="", value=main_config["description"], inline=True)
        # embed.add_field(name="", value="\tДень: " + (await self._get_cycles()).__str__(), inline=True)
        # embed.add_field(name="", value="\tСезон: " + self.chester_bot.replies[await self._get_season()], inline=True)
        # embed.add_field(name="", value="\tВремя суток: " + self.chester_bot.replies[await self._get_day_phase()], inline=True)
        embed.add_field(name="", value=description, inline=False)
        return embed

    async def reload_data(self):
        pass

    # a = [что_класть (if условие else что_класть) цикл (условие-фильтр)]
