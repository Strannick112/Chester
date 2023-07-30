import re

from chesterbot import main_config


class Player:
    def __init__(self, discord_nickname: str, dst_nickname: str):
        self.discord_nickname = discord_nickname.__str__()
        self.dst_nickname = dst_nickname

    @staticmethod
    def from_dict(raw_dict):
        return Player(raw_dict["discord_nickname"], raw_dict["dst_nickname"])

    async def is_player_online(self, console_dst_checker):
        _dst_nickname = re.sub(r'\'', r"\\\\\'", self.dst_nickname)
        _dst_nickname = re.sub(r'\"', r"\\\\\"", _dst_nickname)
        screen_name = main_config['short_server_name'] + main_config["worlds"][0]["shard_id"]
        result = await console_dst_checker.check(
            f"""screen -S {screen_name} -X stuff \""""
            """for _, player in pairs(GetPlayerClientTable()) do """
            f"""if player.name == \\\"{_dst_nickname}\\\" """
            """then print(\\\"PlayerName\\\", player.name) end end \n\"""",
            r"PlayerName\s*(" + _dst_nickname + r")\s*",
            main_config["worlds"][0]["shard_id"],
            screen_name,
            "",
            5
        )
        print("result player_name: ", result)
        return result == self.dst_nickname
