import asyncio

from chesterbot.cogs.server_manage.RemoteServerConnector import RemoteServerConnector
from LocalServerConnector import *

class GameServerConnector():
    def __init__(self):
        if main_config["bot_mode"] == "remote":
            self.connector = RemoteServerConnector()
        else:
            self.connector = LocalServerConnector()

    async def restart_server(self):
        """Перезапускает сервер сразу"""
        return await self.connector.restart_server()

    async def soft_restart_server(self):
        """Перезапускает сервер через 1 минуту"""
        return await self.connector.soft_restart_server()

    async def soft_stop_server(self):
        return await self.connector.soft_stop_server()

    async def start_server(self):
        """Запускает сервер"""
        return await self.connector.start_server()

    async def stop_server(self):
        """Останавливает сервер сразу"""
        return await self.connector.stop_server()

    async def soft_world_regenerate(self):
        """Перегенерирует сервер спустя минуту"""
        return await self.connector.soft_world_regenerate()

    async def command(self, command, shard_id):
        """
        Выполняет команды на игровом сервере. Имеет два параметра:
        shard_id - уникальный ид игрового мира, на котором будет выполнена команда. 1 - поверхность, 2 - пещеры, и т д;
        command - собственно команда, которая будет передана на указанный игровой мир.
        """
        return await self.connector.command(command, shard_id)

    async def ban(self, ku_id):
        """
        Банит игрока на игровом сервере. Имеет один параметр:
        ku_id - уникальный klei_id игрока, на которого снизойдет гнев императора.
        """
        return await self.connector.ban(ku_id)

    async def send_message_to_game(self, author: str, text: str):
        """Отправляет сообщение от указанного автора в игру"""
        return await self.connector.send_message_to_game(author, text)
