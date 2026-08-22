import os
import re

import luadata

from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.AchievementsList import achievements_list
from chesterbot.models import SteamAccount


class AchievementsReader():

    def __init__(self, chester_bot):
        self.chester_bot = chester_bot
        self.player_points = []

    def _get_session_folder(self, world_file_name):
        """Получить список всех путей к папкам с сохранениями"""
        parent_dir = main_config.get("path_to_save") + "/" + world_file_name \
             + "/save/session"
        folders = [f for f in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, f))]
        if folders:
            folder_name = folders[0]
            full_path = os.path.join(parent_dir, folder_name)
            return full_path
        return None

    def _get_latest_file(self, ku_id):
        """Получить актуальный файл сохранения из папки с сохранениями игрока"""
        parent_dirs = []
        for world in main_config.get("worlds"):
            session_folder = self._get_session_folder(world.get("folder_name"))
            player_folders = self._get_player_folders(session_folder)
            for player_folder in player_folders:
                local_ku_id = os.path.basename(player_folder)[:-1]
                if local_ku_id == ku_id:
                    parent_dirs.append(player_folder)
                    break
        files = []
        for parent_dir in parent_dirs:
            files += [
                entry for entry in os.scandir(parent_dir)
                if entry.is_file() and not entry.name.endswith('.meta') and not entry.name == "savelocation"
            ]
        if not files:
            return None
        latest_file = max(files, key=lambda e: e.stat().st_mtime)
        return latest_file.path

    def _get_player_folders(self, session_folder):
        """Получить список всех сохранений с определенного шарда"""
        return [
            full_path for f in os.listdir(session_folder)
            if os.path.isdir(full_path := os.path.join(session_folder, f))
        ]

    def get_player_saves(self, key = lambda x: True):
        """Получить список путей к актуальным файлам сохранения игрока"""
        session_folder = self._get_session_folder(main_config.get("worlds")[0].get("folder_name"))
        player_folders = self._get_player_folders(session_folder)
        player_saves = []
        for player_folder in player_folders:
            ku_id = os.path.basename(player_folder)[:-1]
            if key(ku_id):
                player_saves.append( (ku_id, self._get_latest_file(ku_id)) )
        return player_saves

    async def update_players_points(self):
        """Посчитать рейтинг каждого игрока"""
        self.player_points = []
        for ku_id, file_name in self.get_player_saves():
            if player_info := await self.get_player_points(ku_id, file_name):
                self.player_points.append(player_info)
        self.player_points = [
            player for player in self.player_points
            if (val := player.get("Очки")) is not None and val > 200
        ]
        self.player_points.sort(key=lambda player: player["Очки"], reverse=True)

    async def get_player_points(self, ku_id, file_name):
        """Получить количество очков для конкретного игрока"""
        if file_name is None:
            return None
        if (player_name := await self.get_player_name(ku_id)) is None:
            return None
        return {
            "Никнейм": player_name,
            "Очки": self.calculate_points(AchievementsReader.get_player_stat(await self.get_player_raw_info(file_name))),
            "ku_id": ku_id,
        }

    @staticmethod
    def calculate_points(stat_info):
        """Расчитать количество очков для одного игрока"""
        return sum(stat for stat in stat_info.values() if stat is not None)

    @staticmethod
    def get_player_stat(stat_info):
        """Получить статистику очков для игроков"""
        stat = dict()
        actual_points = 0
        for field_name, field_value in stat_info.items():
            if (points := achievements_list.get(field_name)) is not None:
                if isinstance(field_value, dict):
                    actual_points = points
                else:
                    if field_name == "numSurvivedDay":
                        actual_points = field_value * points
                    else:
                        actual_points = min(field_value, 1) * points
            stat[field_name] = actual_points
        return stat

    async def get_player_name(self, ku_id):
        """Получить никнейм игрока по его уникальному ku_id"""
        player_name = None
        async with self.chester_bot.async_session() as session:
            async with session.begin():
                player = (await SteamAccount.get_by_ku_id(session=session, ku_id=ku_id))
                if player is not None:
                    player_name = player.nickname
        return player_name

    @staticmethod
    async def get_player_raw_info(file_name):
        """Считать информацию из файла сохранения для конкретного игрока"""
        with open(file_name, 'rb') as file:
            content = file.read()
            text = content.decode('utf-8', errors='ignore')
            index = text.find("return")
            if index != -1:
                text = text[index:]
            counter_scobok = 0
            index = 0
            start = text.find('{')
            text = text[start:]
            for letter in text:
                if letter == '{':
                    counter_scobok += 1
                if letter == '}':
                    counter_scobok -= 1
                if counter_scobok == 0 and index != 0:
                    break
                index += 1
            text = text[:index + 1]
            fixed_lua = re.sub(r'([0-9]+\.?[0-9]*)e(-?[0-9]+)', r'0', text)
            return luadata.unserialize(fixed_lua)["data"]["kaachievementmanager"]