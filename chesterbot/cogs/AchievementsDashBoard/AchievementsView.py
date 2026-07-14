import discord

from chesterbot import main_config


class AchievementsView(discord.ui.View):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.column_size = 32

    def column_size_corrector(self, column_headers):
        return [
            header + ' ' * max(self.column_size - len(header), 0)
            for header in column_headers
        ]

    async def _make_dashboard(self):
        embed = discord.Embed(color=0x2F3136, title="РЕЙТИНГОВАЯ ТАБЛИЦА")
        headers = self.column_size_corrector((
            "Сезон: 1",
            "",
            "",
        ))
        for header in headers:
            embed.add_field(name="", value=header, inline=True)
        # embed.add_field(name="", value="Сезон: 1\n", inline=True)
        # embed.add_field(name="", value="Обновлен: 26.04.2024\n", inline=True)
        # embed.add_field(name="", value="До конца сезона: 26\n", inline=True)
        embed.add_field(name="", value="\n", inline=False)
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
        embed.add_field(name="", value=player_nickname_column, inline=True)
        embed.add_field(name="", value=player_points_column, inline=True)
        embed.add_field(name="", value=rangs_column, inline=True)
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
