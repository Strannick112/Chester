from typing import Optional

from sqlalchemy import ForeignKey, select, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class WipeAchievements(Base):
    __tablename__ = "wipe_achievements"

    wipe_id: Mapped[int] = mapped_column(ForeignKey("wipe.id"), primary_key=True)
    wipe: Mapped[Optional["Wipe"]] = relationship("Wipe", back_populates="wipe_achievements")

    id: Mapped[int] = mapped_column(ForeignKey("steam_account.id"), primary_key=True)
    steam_account: Mapped[Optional["SteamAccount"]] = relationship("SteamAccount", back_populates="wipe_achievements")

    score: Mapped[str] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return f"WipeAchievements(wipe_id={str(self.wipe_id)!r}, steam_account_id={str(self.steam_account_id)!r}, score={str(self.score)!r})"

    @staticmethod
    async def create_or_update(session, wipe_id, steam_account_id, score):
        instance = (await session.execute(select(WipeAchievements).filter_by(
            wipe_id=wipe_id, steam_account_id=steam_account_id)
        )).scalars().first()
        if instance:
            instance.score = score
        else:
            instance = WipeAchievements(wipe_id=wipe_id, steam_account_id=steam_account_id, score=score)
            session.add(instance)
        await session.flush()
        return instance
