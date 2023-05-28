import asyncio
import re
import subprocess
import sys
import traceback

from discord.ext import tasks

from chesterbot import ChesterBot


class ConsoleDSTChecker:
    __commands =  {}
    def __init__(self, worlds):
        self.__loop = None
        self.worlds = worlds

    async def on_ready(self, loop):
        self.__loop = loop
        for world in self.worlds:
            self.__checker.start(world["shard_id"], world["file_poll"], world["file_iterator"])

    async def check(self, command: str, reg_answer: str, shard_id: int, screen_name: str):
        screen_list = subprocess.run(
            'screen -ls',
            shell=True,
            stdout=subprocess.PIPE,
            stdin=subprocess.PIPE
        ).stdout.decode('ascii')
        for world in self.worlds:
            if world["shard_id"] == shard_id and screen_name in screen_list:
                try:
                    self.__commands[reg_answer] = {"future": self.__loop.create_future(), "shard_id": shard_id}
                    asyncio.ensure_future(self.__commands[reg_answer]["future"])
                    subprocess.check_output(command, shell=True)
                    return await self.__commands[reg_answer]["future"]
                except Exception as error:
                    print(error)
                break

    @tasks.loop(seconds=0.1)
    async def __checker(self, shard_id, file_poll, file_iter):
        """Следить за логами на игровом сервере"""
        if file_poll.poll(1):
            print("meaw")
            try:
                text = file_iter.stdout.readline()[12:]
                print("Commands is: ", self.__commands)
                for reg_answer, command in self.__commands.items():
                    if command["shard_id"] == shard_id:
                        print("The command is: ", command)
                        print("The shard id is: ", shard_id)
                        print("The reg_answer is: ", reg_answer)
                        print("The text in __checker: ", text)
                        print("The result if finding: ", re.findall(reg_answer, text))
                        if re.findall(reg_answer, text):
                            # print("The result if finding: ", re.findall(reg_answer, text))
                            # print("The reg_answer is: ", reg_answer)
                            print("SUCCESS!")
                            command["future"].set_result(text)
                            # print(command["future"].result())
                            # print("The text in __checker: ", text)
                            break
            except Exception as error:
                print(error)
                print(repr(traceback.extract_tb(sys.exception().__traceback__)))
