import os
import re

import luadata

from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.AchievementsList import achievements_list
from chesterbot.models import SteamAccount


class AchievementsReader():

    def __init__(self, chester_bot):
        self.chester_bot = chester_bot
        self._session_folder = self._get_session_folder()
        self.player_points = []

    def _get_session_folder(self):
        parent_dir = main_config.get("path_to_save") + "/" + main_config.get("worlds")[0].get("folder_name") \
             + "/save/session"
        folders = [f for f in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, f))]
        if folders:
            folder_name = folders[0]
            full_path = os.path.join(parent_dir, folder_name)
            return full_path
        return None

    def _get_latest_file(self, parent_dir):
        files = [
            entry for entry in os.scandir(parent_dir)
            if entry.is_file() and not entry.name.endswith('.meta') and not entry.name == "savelocation"
        ]
        if not files:
            return None
        latest_file = max(files, key=lambda e: e.stat().st_mtime)
        return latest_file.path

    def get_player_saves(self, key = lambda x: True):
        player_folders = [
            full_path for f in os.listdir(self._session_folder)
            if os.path.isdir(full_path := os.path.join(self._session_folder, f))
        ]
        player_saves = []
        for player_folder in player_folders:
            ku_id = os.path.basename(player_folder)[:-1]
            if key(ku_id):
                player_saves.append( (ku_id, self._get_latest_file(player_folder)) )
        return player_saves

    async def update_players_points(self):
        self.player_points = []
        for ku_id, file_name in self.get_player_saves():
            if player_info := await self.get_player_points(ku_id, file_name):
                self.player_points.append(player_info)
        self.player_points = [
            player for player in self.player_points
            if (val := next(iter(player.values()))) is not None and val > 200
        ]
        self.player_points = sorted(self.player_points, key=lambda player: next(iter(player.values())), reverse=True)

    async def get_player_points(self, ku_id, file_name):
        if file_name is None:
            return None
        if (player_name := await self.get_player_name(ku_id)) is None:
            return None
        return {player_name: self.calculate_points(await self.get_player_raw_info(file_name))}

    @staticmethod
    def calculate_points(stat_info):
        return sum(val for d in AchievementsReader.get_player_stat(stat_info) for val in d.values() if val is not None)

    @staticmethod
    def get_player_stat(stat_info):
        stat = []
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
            stat.append((field_name, actual_points))
            print(f"after: {field_name}: field_value: {field_value}, points: {points}, actual_points: {actual_points}")
        return stat

    async def get_player_name(self, ku_id):
        player_name = None
        async with self.chester_bot.async_session() as session:
            async with session.begin():
                player = (await SteamAccount.get_by_ku_id(session=session, ku_id=ku_id))
                if player is not None:
                    player_name = player.nickname
        return player_name

    @staticmethod
    async def get_player_raw_info(file_name):
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
            # print(f"fixed_lua: {fixed_lua}")
            return luadata.unserialize(fixed_lua)["data"]["kaachievementmanager"]