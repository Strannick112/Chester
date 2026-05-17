import os
import json
import re

import luadata

from chesterbot import main_config
from chesterbot.cogs.AchievementsDashBoard.AchievementsList import achievements_list

class AchievementsReader():

    def __init__(self):
        self.session_folder = self.get_session_folder()
        self.player_saves = self.get_player_saves()
        self.player_points = self.get_player_points()

    def get_session_folder(self):
        parent_dir = main_config.get("path_to_save") + "/" + main_config.get("worlds")[0].get("folder_name") \
             + "/save/session"
        folders = [f for f in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, f))]
        if folders:
            folder_name = folders[0]
            full_path = os.path.join(parent_dir, folder_name)
            return full_path
        return None

    def get_player_saves(self):
        player_folders = [
            full_path for f in os.listdir(self.session_folder)
            if os.path.isdir(full_path := os.path.join(self.session_folder, f))
        ]
        player_saves = []
        for player_folder in player_folders:
            player_saves.append(self.get_latest_file(player_folder))
        return player_saves

    def get_latest_file(self, parent_dir):
        files = [
            entry for entry in os.scandir(parent_dir)
            if entry.is_file() and not entry.name.endswith('.meta')
        ]
        if not files:
            return None
        latest_file = max(files, key=lambda e: e.stat().st_mtime)
        return latest_file.path

    def get_player_points(self):
        player_points = []
        data = None
        for file_name in self.player_saves:
            with open(file_name, 'rb') as file:
                content = file.read()
                text = content.decode('utf-8', errors='ignore')
                start = text.find('{')
                end = text.rfind('}')
                clean_json = text[start:end]
                end = clean_json.rfind('}')
                clean_json = clean_json[:end + 1]
                fixed_lua = re.sub(r'([0-9]+\.?[0-9]*)e(-?[0-9]+)', r'0', clean_json)
                data = luadata.unserialize(fixed_lua)["data"]["kaachievementmanager"]
                #data = json.loads(json_content.decode('utf-8'))["data"]["kaachievementmanager"]
                # data = json.load(file)["data"]["kaachievementmanager"]
            cur_points = 0
            for field_name, field_value in data.items():
                if (points := achievements_list.get(field_name)) is not None:
                    if isinstance(field_value, dict):
                        cur_points += points
                    else:
                        cur_points += field_value * points
            player_points.append( { "player_name": cur_points } )
        return player_points
