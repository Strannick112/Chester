from chesterbot import main_config


class AchievementsModel:
    def __init__(self):
        self._data = []

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
        return self._data