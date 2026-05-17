from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.AchievementsReader import AchievementsReader


class AchievementsModel:
    def __init__(self):
        self._data = []
        self.reader = AchievementsReader()

    async def update_data(self):
        self._data = []
        for player_info in self.reader.player_points:
            nick, points = next(iter(player_info.items()))
            print(f"""meaw: { { "Никнейм": nick, "Очки": str(points) } }""")
            self._data.append({ "Никнейм": nick, "Очки": str(points) })
        print(f"self._data: {self._data}")

    async def get_data(self):
        await self.reader.update_player_points()
        await self.update_data()
        return self._data
