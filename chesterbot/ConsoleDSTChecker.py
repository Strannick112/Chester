import asyncio
import codecs
import os
import re
import subprocess

from discord.ext import tasks

from chesterbot import main_config


class ConsoleDSTChecker:

    def __init__(self, worlds):
        self.__loop = None
        self.worlds = worlds
        self.__all_commands = {}
        for world in worlds:
            self.__all_commands[world["shard_id"]] = {}

        self.potential_ban_ku_id = None

    async def on_ready(self, loop):
        self.__loop = loop
        for world in self.worlds:
            self.__checker.start(self.__all_commands[world["shard_id"]], world)
            self.__log_file_check.start(world)

    def simple_check(
            self, command: str, reg_answer: str, default_answer: str, timeout: int
    ):
        return asyncio.create_task(
            self.check_selected_world(
                command, reg_answer, self.worlds[0]["shard_id"], self.worlds[0]["screen_name"], default_answer, timeout
            )
        )

    async def check_selected_world(
            self, command: str, reg_answer: str, shard_id: int, screen_name: str, default_answer: str, timeout: int
    ):
        try:
            screen_list = subprocess.run(
                'screen -ls',
                shell=True,
                stdout=subprocess.PIPE,
                stdin=subprocess.PIPE
            ).stdout.decode('ascii')
            for world in self.worlds:
                if world["shard_id"] == shard_id and screen_name in screen_list:
                    self.__all_commands[shard_id][reg_answer] = self.__loop.create_future()
                    asyncio.ensure_future(self.__all_commands[shard_id][reg_answer])
                    command = f'''screen -S {screen_name} -X stuff "''' + command + '''\n"'''
                    subprocess.call(command, shell=True)
                    result = await asyncio.wait_for(self.__all_commands[shard_id][reg_answer], timeout)
                    return result
            else:
                return default_answer
        except Exception as error:
            print(error)
            return default_answer

    def check_all_worlds(
            self, command: str, reg_answer: str, default_answer: str, timeout: int
    ):
        local_tasks = set()
        for world in self.worlds:
            local_tasks.add(
                asyncio.create_task(
                    self.check_selected_world(
                        command,
                        reg_answer,
                        world["shard_id"], world["screen_name"], default_answer, timeout
                    )
                )
            )
        return local_tasks

    @tasks.loop(seconds=15)
    async def __log_file_check(self, world):
        size_of_log_file = os.path.getsize(world['full_path_to_server_log_file'])
        if size_of_log_file < world["file_log_size"]:
            world["file_log_iter"].close()
            world["file_log_iter"] = codecs.open(world["full_path_to_server_log_file"], "r", encoding="utf-8")
            world["file_log_iter"].seek(0, 2)
        world["file_log_size"] = size_of_log_file

    @tasks.loop(seconds=0.01)
    async def __checker(self, commands, world):
        """Следить за логами на игровом сервере"""
        try:
            if text := world["file_log_iter"].readline()[12:]:
                if "Client authenticated" in text:
                    await main_config['log_channel'].send(content=("```" + text + "```"))

                # Против ддос атаки, возникающей, когда клиент пытается отсоединиться от сервера, но не присылает данных
                if "disconnected from [SHDMASTER](1)" in text:
                    if potential_ban_ku_id := re.findall("(\(KU_.+?\))", text)[0]:
                        self.potential_ban_ku_id = potential_ban_ku_id
                        return
                if "[ID_DST_CLIENT_READY] no client object present, closing client connection" in text:
                    if self.potential_ban_ku_id:
                        text = re.sub(r'\"', r"\"", re.sub(r'\'', r"\'", f"TheNet:Ban(\"{self.potential_ban_ku_id}\")"))
                        await main_config['log_channel'].send(content="Выполнение команды «" + text + "» принято к исполнению")

                        subprocess.check_output(
                            f"""screen -S {main_config['short_server_name'] + main_config["worlds"][0]["shard_id"]} -X stuff""" +
                            f""" "{text}\n\"""",
                            shell=True
                        )
                        self.potential_ban_ku_id = None
                for keys, command in commands.items():
                    try:
                        if not command.done():
                            if result := re.findall(keys, text):
                                command.set_result(result[0])
                            break
                    except Exception as error:
                        print(error)
                        print("The command is: ", command)
                        print("The shard id is: ", keys)
                        print("The text in __checker: ", text)
                        print("The result if finding: ", re.findall(keys, text))
        except Exception as error:
            print(error)
