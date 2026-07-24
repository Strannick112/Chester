from chesterbot.cogs.AchievementsDashBoard.AchievementsReader import AchievementsReader


class AchievementsModel:
    def __init__(self, chester_bot):
        self._data = []
        self.reader = AchievementsReader(chester_bot)

    async def update_data(self):
        self._data = []
        print("meaw14")
        for player_info in self.reader.player_points:
            nick, points = next(iter(player_info.items()))
            # print(f"""meaw: { { "Никнейм": nick, "Очки": str(points) } }""")
            self._data.append({ "Никнейм": nick, "Очки": str(points) })
        print("meaw15")
        # print(f"self._data: {self._data}")

    async def get_data(self):
        print("meaw10")
        await self.reader.update_player_points()
        print("meaw11")
        await self.update_data()
        print("meaw13")
        return self._data
