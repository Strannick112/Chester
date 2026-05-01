import discord
from discord.ext import tasks

from chesterbot import main_config


class AchievementsModel:
    def __init__(self):
        self.data = []

    async def update_data(self):
        self.data = [
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
