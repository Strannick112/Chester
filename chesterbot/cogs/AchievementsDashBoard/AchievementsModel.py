from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.AchievementsReader import AchievementsReader


class AchievementsModel:
    def __init__(self):
        self._data = []
        self.reader = AchievementsReader()

    async def update_data(self):
        self._data = [
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 },
            { "Никнейм": "Nickname", "Очки": 0 }
        ]

    async def get_data(self):
        await self.update_data()
        self.reader.get_session_folder()
        self.reader.get_player_saves()
        return self._data

