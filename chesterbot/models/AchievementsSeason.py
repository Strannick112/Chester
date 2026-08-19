from typing import List

from sqlalchemy import select, func, and_
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
                .where(and_(AchievementsSeason.id == last_season_id, WipeAchievements.score > 200))
                .group_by(SteamAccount.ku_id, SteamAccount.nickname)
                .order_by(func.sum(WipeAchievements.score).desc())
            )).all()
        return [ { "Никнейм": row.nickname, "Очки": row.score, "ku_id": row.ku_id } for row in instance ]

    @staticmethod
    async def get_last_season(session):
        return (await session.execute(
            select(AchievementsSeason)
            .order_by(AchievementsSeason.id.desc())
            .limit(1)
        )).scalars().first()

    @staticmethod
    async def start_new_season(session):
        count_of_wipes_by_last_season = (await session.execute(
            select(func.count(Wipe.id))
            .where(Wipe.achievements_season_id == (await AchievementsSeason.get_last_season(session)).id)
        )).scalar()
        print("Count of Wipes by last season:", count_of_wipes_by_last_season)
        # if count_of_wipes_by_last_season == 2:
        #     session.add(AchievementsSeason())
        #     session.flush()
