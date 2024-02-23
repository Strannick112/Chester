import re
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from chesterbot import main_config
from chesterbot.ConsoleDSTChecker import ConsoleDSTChecker
from .Base import Base


class Claim(Base):
    __tablename__ = "claim"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    player: Mapped[Optional["Player"]] = relationship("Player", back_populates="claim")

    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"), default=1)
    status: Mapped[Optional["Status"]] = relationship("Status", back_populates="claim")

    wipe_id: Mapped[int] = mapped_column(ForeignKey("wipe.id"))
    wipe: Mapped[Optional["Wipe"]] = relationship("Wipe")

    started: Mapped[int] = mapped_column(DateTime, default=datetime.utcnow)
    approved: Mapped[int] = mapped_column(DateTime, default=datetime.utcnow)
    executed: Mapped[int] = mapped_column(DateTime, default=datetime.utcnow)

    item: Mapped[List["Item"]] = relationship("Item",
        secondary='claim_item', back_populates="claim"
    )

    def __repr__(self) -> str:
        return f"Claim(id={str(self.id)!r}, player_id={str(self.player_id)!r}," + \
            f" status_id={str(self.status_id)!r}, wipe_id={str(self.wipe_id)!r}," + \
            f" started={str(self.started)!r}, approved={str(self.approved)!r}," + \
            f" executed={str(self.executed)!r})"

    @staticmethod
    def get_or_create(session, item, **kwargs):
        # with session.begin():
        instance = session.query(Claim).filter_by(**kwargs).first()
        if instance:
            pass
        else:
            instance = Claim(item=item, **kwargs)
            session.add(instance)
        # session.close()
        return instance

    async def check_days(self, console_dst_checker: ConsoleDSTChecker, is_ok: int):
        dst_nickname = re.sub(r'\'', r"\\\\\'", self.player.steam_account.nickname)
        dst_nickname = re.sub(r'\"', r"\\\\\"", dst_nickname)
        raw_results = set()
        for world in main_config["worlds"]:
            command = f"""screen -S {world["screen_name"]} -X stuff""" \
                      f""" "for k,v in pairs(AllPlayers) do print('CheckDaysForPlayer: ', v.name, TheNet:GetClientTableForUser(v.userid).playerage) end\n\""""
            raw_results.add(
                await console_dst_checker.check(
                    command,
                    r'CheckDaysForPlayer:\s+' + dst_nickname + r'\s+([\d]+)',
                    world["shard_id"], world["screen_name"], "0", 5
                )
            )
        for result in raw_results:
            if int(result) > 0:
                return int(result)
        return 0