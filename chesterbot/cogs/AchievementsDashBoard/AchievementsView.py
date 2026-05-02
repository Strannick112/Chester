import discord

from chesterbot import main_config


class AchievementsView(discord.ui.View):
    def __init__(self, model):
        super().__init__()
        self.model = model

    async def _make_dashboard(self):
        embed = discord.Embed(color=0x2F3136, title="Прогресс игроков")
        description = ""
        data = await self.model.get_data()
        for player in data:
            print(f"Nick: {player.get('Никнейм')}")
            description += player.get("Никнейм")
            description += "\t"
            print(f"Points: {player.get('Очки')}")
            description += player.get("Очки")
        embed.add_field(name="", value=description, inline=False)
        return embed

    async def update(self):
        embeds = [await self._make_dashboard()]

        # view = discord.ui.View()
        # style = discord.ButtonStyle.gray
        # for button_description in main_config["buttons"]:
        #     view.add_item(
        #         item=discord.ui.Button(
        #             style=style, label=button_description["description"],
        #             url=button_description["url"]
        #         )
        #     )

        # return { "embeds": embeds, "view": view }
        return { "embeds": embeds }
