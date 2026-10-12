from typing import Optional

from sqlalchemy import ForeignKey, select, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Wipe import Wipe
from .SteamAccount import SteamAccount

# from . import Wipe, SteamAccount
from .Base import Base


class WipeAchievements(Base):
    __tablename__ = "wipe_achievements"

    wipe_id: Mapped[int] = mapped_column(ForeignKey("wipe.id"), primary_key=True)
    wipe: Mapped[Optional["Wipe"]] = relationship("Wipe", back_populates="wipe_achievements")

    steam_account_id: Mapped[int] = mapped_column(ForeignKey("steam_account.id"), primary_key=True)
    steam_account: Mapped[Optional["SteamAccount"]] = relationship("SteamAccount", back_populates="wipe_achievements")

    score: Mapped[str] = mapped_column(BigInteger)

    additional_points: Mapped[str] = mapped_column(BigInteger)
    def __repr__(self) -> str:
        return f"WipeAchievements(wipe_id={str(self.wipe_id)!r}, steam_account_id={str(self.steam_account_id)!r},"\
               " score={str(self.score)!r}, additional_points={str(self.additional_points)!r})"

    @staticmethod
    async def create_or_update(session, wipe_id, steam_account_id, score = None, additional_points = None):
        instance = (await session.execute(select(WipeAchievements).filter_by(
            wipe_id=wipe_id, steam_account_id=steam_account_id)
        )).scalars().first()
        if instance:
            if score is not None:
                instance.score = score
            if additional_points is not None:
                instance.additional_points = additional_points
        else:
            instance = WipeAchievements(
                wipe_id=wipe_id, steam_account_id=steam_account_id,
                score=score if score is not None else 0,
                additional_points=additional_points if additional_points is not None else 0
            )
            session.add(instance)
        await session.flush()
        return instance

    @staticmethod
    async def add_points(session, ku_id, additional_points):
        instance = (await session.execute(select(WipeAchievements).filter_by(
            wipe_id=(await Wipe.get_last_stopped_wipe(session)).id,
            steam_account_id=(await SteamAccount.get_by_ku_id(session, ku_id)).id)
        )).scalars().first()
        if instance:
            instance.additional_points += additional_points
            await session.flush()
            return True
        return False

    @staticmethod
    async def remove_points(session, ku_id, additional_points):
        instance = (await session.execute(select(WipeAchievements).filter_by(
            wipe_id=(await Wipe.get_last_stopped_wipe(session)).id,
            steam_account_id=(await SteamAccount.get_by_ku_id(session, ku_id)).id)
        )).scalars().first()
        if instance:
            instance.additional_points -= additional_points
            await session.flush()
            return True
        return False