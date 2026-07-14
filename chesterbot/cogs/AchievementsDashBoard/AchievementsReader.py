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

    def _get_player_saves(self):
        player_folders = [
            full_path for f in os.listdir(self._session_folder)
            if os.path.isdir(full_path := os.path.join(self._session_folder, f))
        ]
        print(f"player_folders: {player_folders}")
        player_saves = []
        for player_folder in player_folders:
            player_saves.append( (os.path.basename(player_folder)[:-1], self._get_latest_file(player_folder)) )
        print(f"player_saves: {player_saves}")
        return player_saves

    async def update_player_points(self):
        self.player_points = []
        data = None
        for ku_id, file_name in self._get_player_saves():
            print(f"ku_id: {ku_id}")
            print(f"file_name: {file_name}")

            player_name = None
            async with self.chester_bot.async_session() as session:
                async with session.begin():
                    player = ( await SteamAccount.get_by_ku_id(session=session, ku_id=ku_id) )
                    print(f"player: {player}")
                    if player is not None:
                        player_name = player.nickname
            print(f"player_name: {player_name}")
            if player_name is None:
                continue

            print(f"meaw before open file")
            with open(file_name, 'rb') as file:
                print(f"meaw inside open file")
                content = file.read()
                print("1")
                text = content.decode('utf-8', errors='ignore')
                print("2")
                start = text.find('{')
                print("3")
                end = text.rfind('}')
                print("4")
                clean_json = text[start:end]
                print("5")
                end = clean_json.rfind('}')
                print("6")
                clean_json = clean_json[:end + 1]
                print("7")
                fixed_lua = re.sub(r'([0-9]+\.?[0-9]*)e(-?[0-9]+)', r'0', clean_json)
                print("8")
                data = luadata.unserialize(fixed_lua)["data"]["kaachievementmanager"]
                print("9")
            cur_points = 0
            print(f"meaw after close file")
            for field_name, field_value in data.items():
                if (points := achievements_list.get(field_name)) is not None:
                    if isinstance(field_value, dict):
                        cur_points += points
                    else:
                        cur_points += field_value * points
            print(f"cur_points: {cur_points}")

            self.player_points.append( { player_name: cur_points } )
