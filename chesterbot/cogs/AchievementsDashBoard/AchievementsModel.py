from chesterbot.cogs.AchievementsDashBoard.AchievementsReader import AchievementsReader


class AchievementsModel:
    def __init__(self, chester_bot):
        # self._data = []
        self.reader = AchievementsReader(chester_bot)

    # async def update_data(self):
    #     self._data = []
    #     for player_info in self.reader.player_points:
    #         nick, points = next(iter(player_info.items()))
    #         self._data.append({ "Никнейм": nick, "Очки": str(points) })

    async def get_data(self):
        await self.reader.update_players_points()
        # await self.update_data()
        return self.reader.player_points
