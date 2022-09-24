import codecs


class Player:
    def __init__(self, discord_nickname: str, dst_nickname: str):
        self.discord_nickname = discord_nickname.__str__()
        self.dst_nickname = dst_nickname

    @staticmethod
    def from_dict(raw_dict):
        return Player(raw_dict["discord_nickname"], raw_dict["dst_nickname"])
