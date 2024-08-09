import asyncio
import codecs
import os
import re
import subprocess

from discord.ext import tasks


class ConsoleDSTChecker:

    def __init__(self, worlds):
        self.__loop = None
        self.worlds = worlds
        self.__all_commands = {}
        for world in worlds:
            self.__all_commands[world["shard_id"]] = {}

    async def on_ready(self, loop):
        self.__loop = loop
        for world in self.worlds:
            self.__checker.start(self.__all_commands[world["shard_id"]], world)
            self.__log_file_check.start(world)

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

    async def check_all_worlds(
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
