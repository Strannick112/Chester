import discord

from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.RangList import rang_list


class AchievementsView:
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.column_size = 13

    def column_size_corrector(self, column_headers):
        return [
            header + '⠀' * max(self.column_size - len(header), 0)
            for header in column_headers
        ]

    async def _make_dashboard(self):
        # print("meaw1")
        # embed = discord.Embed(color=0x2F3136, title="РЕЙТИНГ ИГРОКОВ")
        embed = discord.Embed(color=0x2F3136, title="")
        # print("meaw2")
        # embed.set_thumbnail(url=main_config["achievements_tumbnail"])
        # print("meaw3")
        # headers = self.column_size_corrector((
        #     "Сезон: 1",
        #     "",
        #     "",
        # ))
        headers = self.column_size_corrector((
            "",
            "",
            "",
        ))
        # print("meaw4")
        for header in headers:
            embed.add_field(name="", value=header, inline=True)
        # print("meaw5")
        # embed.add_field(name="", value="Сезон: 1\n", inline=True)
        # embed.add_field(name="", value="Обновлен: 26.04.2024\n", inline=True)
        # embed.add_field(name="", value="До конца сезона: 26\n", inline=True)
        embed.add_field(name="", value="\n", inline=False)
        # print("meaw6")
        data = await self.model.get_data()
        # print("meaw7")
        player_nickname_column = ""
        player_points_column = ""
        rangs_column = ""
        # print("meaw2")
        for player in data:
            points = player.get('Очки')
            player_nickname_column += player.get("Никнейм")
            player_nickname_column += "\n"
            player_points_column += f"⠀⠀⠀Очки: {str(points)}"
            player_points_column += "\n"
            cur_rang = ""
            for rang_info in rang_list.items():
                if int(rang_info[1]) < int(points):
                    cur_rang = rang_info[0]
                else:
                    break
            # print(f"cur_rang: {cur_rang}")
            rangs_column += f"⠀⠀Ранг: {cur_rang}"
            rangs_column += "\n"
        embed.add_field(name="", value=player_nickname_column, inline=True)
        embed.add_field(name="", value=player_points_column, inline=True)
        embed.add_field(name="", value=rangs_column, inline=True)
        return embed

    async def update(self):
        embed = discord.Embed(color=0x2F3136, title="РЕЙТИНГ ИГРОКОВ")
        # print("meaw2")
        embed.set_thumbnail(url=main_config["achievements_tumbnail"])
        # print("meaw3")
        headers = self.column_size_corrector((
            "Сезон: 1",
            "",
            "",
        ))
        embeds = [embed, await self._make_dashboard()]

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
