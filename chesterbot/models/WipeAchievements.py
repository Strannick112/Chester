from typing import Optional

from sqlalchemy import ForeignKey, select, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class WipeAchievements(Base):
    __tablename__ = "achievements_history"

    wipe_id: Mapped[int] = mapped_column(ForeignKey("wipe.id"))
    wipe: Mapped[Optional["Wipe"]] = relationship("Wipe", back_populates="achievements_history")

    steam_account_id: Mapped[int] = mapped_column(ForeignKey("steam_account.id"))
    steam_account: Mapped[Optional["SteamAccount"]] = relationship("SteamAccount", back_populates="achievements_history")

    score: Mapped[str] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return f"WipeAchievements(wipe_id={str(self.wipe_id)!r}, steam_account_id={str(self.steam_account_id)!r}, score={str(self.score)!r})"

    @staticmethod
    async def create_or_update(session, wipe_id, steam_account_id, points):
        instance = (await session.execute(select(WipeAchievements).filter_by(
            wipe_id=wipe_id, steam_account_id=steam_account_id)
        )).scalars().first()
        if instance:
            instance.points = points
        else:
            instance = WipeAchievements(wipe_id=wipe_id, steam_account_id=steam_account_id, points=points)
            session.add(instance)
        await session.flush()
        return instance
