from typing import List

from sqlalchemy import select
from sqlalchemy.orm import relationship, Mapped, mapped_column

from chesterbot.models import Base


class AchievementsSeason(Base):
    __tablename__ = "achievements_season"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    wipes: Mapped[List["Wipe"]] = relationship("Wipe")

    @staticmethod
    async def get_or_create(session, id):
        instance = (await session.execute(select(AchievementsSeason).filter_by(id=id))).scalars().first()
        if instance:
            pass
        else:
            instance = AchievementsSeason(id=id)
            session.add(instance)
        await session.flush()
        return instance
