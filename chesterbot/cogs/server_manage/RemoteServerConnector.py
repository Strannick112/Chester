import aiohttp

from chesterbot import main_config


class RemoteServerConnector():
    def __init__(self):
        self.url = main_config["remote"]["url"]
        self.token = main_config["remote"]["token"]

    async def send_request(self, url, payload = ""):
        """Асинхронно отправляет запрос на перезапуск сервера"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}"
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url + url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        return True
                    else:
                        print(f"❌ Ошибка: {response.status}")
                        error_text = await response.text()
                        print(f"Детали: {error_text}")
                        return False

        except aiohttp.ClientConnectorError:
            print("❌ Не удалось подключиться к серверу")
            return None
        except aiohttp.ClientError as e:
            print(f"❌ Ошибка клиента: {e}")
            return None
        except Exception as e:
            print(f"❌ Неожиданная ошибка: {e}")
            return None

    async def restart_server(self):
        """Перезапускает сервер сразу"""
        return await self.send_request("/restart_server")

    async def soft_restart_server(self):
        """Перезапускает сервер через 1 минуту"""
        return await self.send_request("/soft_restart_server")

    async def soft_stop_server(self):
        """Останавливает сервер через 1 минуту"""
        return await self.send_request("/soft_stop_server")

    async def start_server(self):
        """Запускает сервер"""
        return await self.send_request("/start_server")

    async def stop_server(self):
        """Останавливает сервер сразу"""
        return await self.send_request("/stop_server")

    async def soft_world_regenerate(self):
        """Перегенерирует сервер спустя минуту"""
        return await self.send_request("/soft_world_regenerate")

    async def send_message_to_game(self, author: str, text: str):
        """Отправляет сообщение от указанного автора в игру"""
        return await self.send_request("/send_message_to_game", {"author": author, "text": text})

    async def command(self, command, shard_id = main_config["worlds"][0]["shard_id"]):
        """
        Выполняет команды на игровом сервере. Имеет два параметра:
        shard_id - уникальный ид игрового мира, на котором будет выполнена команда. 1 - поверхность, 2 - пещеры, и т д;
        command - собственно команда, которая будет передана на указанный игровой мир.
        """
        return await self.send_request("/command", {"command": command, "shard_id": shard_id})

    async def ban(self, ku_id):
        """
        Банит игрока на игровом сервере. Имеет один параметр:
        ku_id - уникальный klei_id игрока, на которого снизойдет гнев императора.
        """
        return await self.send_request("/ban", {"ku_id": ku_id})
