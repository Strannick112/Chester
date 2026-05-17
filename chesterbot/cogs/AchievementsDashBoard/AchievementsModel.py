from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.AchievementsReader import AchievementsReader


class AchievementsModel:
    def __init__(self):
        self._data = []
        self.reader = AchievementsReader()

    async def update_data(self):
        self._data = []
        print(f"player_points: {self.reader.player_points}")
        for nick, points in self.reader.player_points:
            self._data.append({ "Никнейм": nick, "Очки": str(points) })

    async def get_data(self):
        await self.reader.update_player_points()
        await self.update_data()
        return self._data
