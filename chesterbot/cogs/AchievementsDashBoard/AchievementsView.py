import discord

from chesterbot import main_config


class AchievementsView(discord.ui.View):
    def __init__(self, model):
        super().__init__()
        self.model = model

    async def _make_dashboard(self):
        print("meaw3")
        embed = discord.Embed(color=0x2F3136, title="РЕЙТИНГОВАЯ ТАБЛИЦА")
        header = "Сезон: 1\tОбновлен: 26.04.2024\tДо конца сезона: 26\n"
        embed.add_field(name="", value=header, inline=True)
        data = await self.model.get_data()
        player_nickname_column = ""
        player_points_column = ""
        rangs_column = ""
        for player in data:
            player_nickname_column += player.get("Никнейм")
            player_nickname_column += "\n"
            player_points_column += f"Очки: {str(player.get('Очки'))}"
            player_points_column += "\n"
            rangs_column += "Ранг: Чемпион"
            rangs_column += "\n"
        embed.add_field(name="Никнейм", value=player_nickname_column, inline=True)
        embed.add_field(name="Очки", value=player_points_column, inline=True)
        embed.add_field(name="Ранги", value=rangs_column, inline=True)
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
