from typing import List

from sqlalchemy import select, func
from sqlalchemy.orm import relationship, Mapped, mapped_column

from chesterbot.models import Base, Wipe, WipeAchievements, SteamAccount


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

    @staticmethod
    async def get_achievements_info(session):
        last_season_id = (await session.execute(
            select(AchievementsSeason)
            .order_by(AchievementsSeason.id.desc())
        )).scalars().first().id
        instance = (
            await session.execute(
                select(SteamAccount.ku_id, SteamAccount.nickname, func.sum(WipeAchievements.score).label('score'))
                .join(AchievementsSeason.wipes)
                .join(Wipe.wipe_achievements)
                .join(WipeAchievements.steam_account)
                .where(AchievementsSeason.id == last_season_id)
                .group_by(SteamAccount.ku_id, SteamAccount.nickname)
                .order_by(func.sum(WipeAchievements.score).desc())
            )).all()
        return [ { "Никнейм": row.nickname, "Очки": row.score, "ku_id": row.ku_id } for row in instance ]
