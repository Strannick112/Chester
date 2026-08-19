from typing import List, Optional

from sqlalchemy import DateTime, func, select, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class Wipe(Base):
    __tablename__ = "wipe"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started: Mapped[int] = mapped_column(DateTime(timezone=True), default=func.now())
    stopped: Mapped[int] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="wipe")

    wipe_achievements: Mapped[List["WipeAchievements"]] = relationship("WipeAchievements")

    achievements_season_id: Mapped[int] = mapped_column(ForeignKey("achievements_season.id"), nullable=True, default=None)
    achievements_season: Mapped[Optional["AchievementsSeason"]] = relationship("AchievementsSeason", back_populates="wipes")

    def __repr__(self) -> str:
        return f"Wipe(id={str(self.id)!r}, started={str(self.started)!r}, stopped={str(self.stopped)!r}, achievements_season_id={str(self.achievements_season_id)!r})"

    async def to_str(self):
        claims = "[\n"
        status_max_lenght = 12
        for index, claim in enumerate(await self.awaitable_attrs.claims):
            claims += f"ᅠᅠ{index + 1}. [Заявка](" + str(claim.message_link) + ")ᅠ"
            status = str((await claim.awaitable_attrs.status).name)
            claims += status + str(((status_max_lenght - len(status))) * " ")
            claims += f"<@" + str(
                (
                    await (await claim.awaitable_attrs.player).awaitable_attrs.discord_account
                ).discord_id) + ">"
            claims += ";\n"
        claims += "]"
        stopped = '?' if self.stopped == self.started else str(self.stopped)
        return (f"Номер вайпа={str(self.id)},\nНомер сезона={str(self.achievements_season_id)},\n"
                f"Начало={str(self.started)},\nКонец={stopped!r},\n"
                f"Заявки={str(claims)}\n")

    @staticmethod
    async def get_or_create(session, **kwargs):
        instance = (await session.execute(select(Wipe).filter_by(**kwargs))).scalars().first()
        if instance:
            pass
        else:
            instance = Wipe(**kwargs)
            session.add(instance)
        await session.flush()
        return instance

    @staticmethod
    async def get_last_wipe(session):
        return (await session.execute(
            select(Wipe)
            .order_by(Wipe.id.desc())
            .limit(1)
        )).scalars().first()

    @staticmethod
    async def get_last_stopped_wipe(session):
        return (await session.execute(
            select(Wipe)
            .where(Wipe.stopped.is_not(None))
            .order_by(Wipe.id.desc())
            .limit(1)
        )).scalars().first()

    @staticmethod
    async def get_wipe_by_id(session, wipe_id):
        return (await session.execute(
            select(Wipe)
            .filter_by(id=wipe_id)
        )).scalars().first()
