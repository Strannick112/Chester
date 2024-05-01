from typing import List, Optional

from sqlalchemy import ForeignKey, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chesterbot import main_config
from chesterbot.ConsoleDSTChecker import ConsoleDSTChecker
from .Base import Base


class Player(Base):
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    steam_account_id: Mapped[int] = mapped_column(ForeignKey("steam_account.id"))
    steam_account: Mapped[Optional["SteamAccount"]] = relationship("SteamAccount", back_populates="player")

    discord_account_id: Mapped[int] = mapped_column(ForeignKey("discord_account.id"))
    discord_account: Mapped[Optional["DiscordAccount"]] = relationship("DiscordAccount", back_populates="player")

    claim: Mapped[List["Claim"]] = relationship("Claim")

    def __repr__(self) -> str:
        return f"Player(id={str(self.id)!r}, steam_account_id={str(self.steam_account_id)!r}, discord_account_id={str(self.discord_account_id)!r})"

    @staticmethod
    async def get_or_create(session, **kwargs):
        if instance := (await session.execute(select(Player).filter_by(**kwargs))).scalars().first():
            return instance
        if instance := (await session.execute(select(Player).filter_by(discord_account_id=kwargs.get("discord_account_id")))).scalars().first():
            instance.steam_account_id = kwargs.get("steam_account_id")
            session.add(instance)
            # await session.flush()
            return instance
        else:
            instance = Player(**kwargs)
            session.add(instance)
        # await session.flush()
        return instance

    async def is_player_online(self, console_dst_checker: ConsoleDSTChecker):
        ku_id = (await self.awaitable_attrs.steam_account).ku_id
        screen_name = main_config['short_server_name'] + main_config["worlds"][0]["shard_id"]
        result = await console_dst_checker.check(
            f"""print(\\\"PlayerID: \\\", LookupPlayerInstByUserID(\\\"{ku_id}\\\").userid)""",
            r"PlayerID:\s*(" + ku_id + r")\s*",
            main_config["worlds"][0]["shard_id"],
            screen_name,
            "",
            5
        )
        return result == (await self.awaitable_attrs.steam_account).ku_id
