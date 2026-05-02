import os

from chesterbot import main_config

class AchievementsReader():

    def __init__(self):
        self.session_folder = self.get_session_folder()
        self.player_saves = self.get_player_saves()

    def get_session_folder(self):
        parent_dir = main_config.get("path_to_save") + "/" + main_config.get("worlds")[0].get("folder_name") \
             + "/save/session"
        folders = [f for f in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, f))]
        if folders:
            folder_name = folders[0]
            full_path = os.path.join(parent_dir, folder_name)
            print(f"Folder path: {full_path}")
            return full_path
        return None

    def get_player_saves(self):
        player_folders = [
            full_path for f in os.listdir(self.session_folder)
            if os.path.isdir(full_path := os.path.join(self.session_folder, f))
        ]
        print("listdir:", os.listdir(self.session_folder))
        print("folders:", len(player_folders))
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
