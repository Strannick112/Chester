import discord

from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.RangList import rang_list


class AchievementsView:
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.column_size = 42

    def column_size_corrector(self, column_headers):
        return [
            header + "\u200b " * max(self.column_size - len(header), 0)
            for header in column_headers
        ]

    async def _make_dashboard(self):
        data = await self.model.get_data()
        players_by_rang = dict()
        for player in data:
            points = player.get('Очки')
            cur_rang = ""
            for rang_info in rang_list.items():
                if int(rang_info[1]) < int(points):
                    cur_rang = rang_info[0]
                else:
                    break
            if players_by_rang.get(cur_rang, None) is None:
                players_by_rang[cur_rang] = [player]
            else:
                players_by_rang[cur_rang].append(player)
        rang_embeds = []
        for rang, players in players_by_rang.items():
            rang_embed = discord.Embed(color=0x2F3136, title="")
            headers = self.column_size_corrector((
                "",
                "",
                "",
            ))
            for header in headers:
                rang_embed.add_field(name="", value=header, inline=True)
            rang_embed.add_field(name="", value="\n", inline=False)
            rang_embed.set_thumbnail(url=main_config["achievement_rang_list"][rang])
            player_nickname_column = ""
            player_points_column = ""
            rangs_column = ""
            for player in players:
                points = player.get('Очки')
                player_nickname_column += player.get("Никнейм")
                player_nickname_column += "\n"
                player_points_column += f"⠀⠀⠀Очки: {str(points)}"
                player_points_column += "\n"
                rangs_column += f"⠀⠀Ранг: {rang}"
                rangs_column += "\n"
            rang_embed.add_field(name="", value=player_nickname_column, inline=True)
            rang_embed.add_field(name="", value=player_points_column, inline=True)
            rang_embed.add_field(name="", value=rangs_column, inline=True)
            rang_embeds.append(rang_embed)
        return rang_embeds

    async def update(self):
        embed = discord.Embed(color=0x2F3136, title="РЕЙТИНГ ИГРОКОВ")
        # embed.set_thumbnail(url=main_config["achievement_embed_law_picture"])
        headers = (
            "Сезон: 1⠀⠀⠀⠀⠀⠀",
            "Порог входа: 200 очков⠀⠀⠀⠀",
            "Завершение: 18.09⠀⠀⠀ㅤㅤㅤ",
        )
        # embed.set_image(url=main_config["achievement_embed_law_picture"])
        for header in headers:
            embed.add_field(name="", value=header, inline=True)
        embeds = [embed, *(await self._make_dashboard())]

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
