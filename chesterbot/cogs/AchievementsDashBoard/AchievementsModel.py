from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.AchievementsReader import AchievementsReader


class AchievementsModel:
    def __init__(self):
        self._data = []
        self.reader = AchievementsReader()

    async def update_data(self):
        self._data = []
        for nick, points in self.reader.player_points:
            self._data.append({ "Никнейм": nick, "Очки": str(points) })

    async def get_data(self):
        await self.update_data()
        await self.reader.update_player_points()
        self.reader.get_session_folder()
        self.reader.get_player_saves()
        return self._data

