from typing import Optional

from sqlalchemy import ForeignKey, select, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class AchievementsHistory(Base):
    __tablename__ = "achievements_history"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    wipe_id: Mapped[int] = mapped_column(ForeignKey("wipe.id"))
    wipe: Mapped[Optional["Wipe"]] = relationship("Wipe", back_populates="achievements_history")

    discord_account_id: Mapped[int] = mapped_column(ForeignKey("discord_account.id"))
    discord_account: Mapped[Optional["DiscordAccount"]] = relationship("DiscordAccount", back_populates="achievements_history")

    score: Mapped[str] = mapped_column(BigInteger)

    def __repr__(self) -> str:
        return f"AchievementsHistory(id={str(self.id)!r}, wipe_id={str(self.wipe_id)!r}, discord_account_id={str(self.discord_account_id)!r}, score={str(self.score)!r})"

    @staticmethod
    async def get_or_create(session, **kwargs):
        instance = (await session.execute(select(AchievementsHistory).filter_by(**kwargs))).scalars().first()
        if instance:
            pass
        else:
            instance = AchievementsHistory(**kwargs)
            session.add(instance)
        await session.flush()
        return instance
