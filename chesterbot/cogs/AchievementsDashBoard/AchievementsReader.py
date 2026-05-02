import os

from sqlalchemy.testing.config import Config

from chesterbot import main_config


class AchievementsReader():

    def __init__(self):
        self.session_folder = self.get_session_folder()

    def get_session_folder(self):
        parent_dir = main_config.get("path_to_save") + "\\" + main_config.get("worlds")[0].get("folder_name") \
             + "\save\session"  # Путь, где лежит ваша папка
        # Список всех папок в этой директории
        folders = [f for f in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, f))]

        if folders:
            folder_name = folders[0]
            full_path = os.path.join(parent_dir, folder_name)
            print(f"Folder path: {full_path}")
            return full_path
        return None
