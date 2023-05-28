import asyncio
import re
import subprocess
import sys
import traceback

from discord.ext import tasks

from chesterbot import ChesterBot


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
            self.__checker.start(self.__all_commands[world["shard_id"]], world["file_log_iter"])

    async def check(self, command: str, reg_answer: str, shard_id: int, screen_name: str, default_answer: int, timeout: int):
        screen_list = subprocess.run(
            'screen -ls',
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        ).stdout.decode('ascii')
        for world in self.worlds:
            if world["shard_id"] == shard_id and screen_name in screen_list:
                try:
                    self.__all_commands[shard_id][reg_answer] = self.__loop.create_future()
                    asyncio.ensure_future(self.__all_commands[shard_id][reg_answer])
                    print("meaw")
                    subprocess.call(command, shell=True)
                    print("gav")
                    try:
                        return await asyncio.wait_for(self.__all_commands[shard_id][reg_answer], timeout)
                    except asyncio.TimeoutError:
                        return default_answer
                except Exception as error:
                    print(error)
                    print(repr(traceback.extract_tb(sys.exception().__traceback__)))
                break

    @tasks.loop(seconds=0.1)
    async def __checker(self, commands, file_log_iter):
        """Следить за логами на игровом сервере"""
        try:
            if text := file_log_iter.readline()[12:]:
                for keys, command in commands.items():
                    try:
                        print("The command is: ", command)
                        print("The shard id is: ", keys)
                        print("The text in __checker: ", text)
                        print("The result if finding: ", re.findall(keys, text))
                        if result := re.findall(keys, text):
                            if not command.done():
                                command.set_result(result[0])
                            break
                    except Exception as error:
                        print(error)
                        print("The command is: ", command)
                        print("The shard id is: ", keys)
                        print("The text in __checker: ", text)
                        print("The result if finding: ", re.findall(keys, text))
                        print(repr(traceback.extract_tb(sys.exception().__traceback__)))
        except Exception as error:
            print(error)
            print(repr(traceback.extract_tb(sys.exception().__traceback__)))
