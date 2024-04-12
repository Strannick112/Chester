from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session

from chesterbot import main_config

statuses = dict()
statuses["not_approved"] = 1
statuses["approved"] = 2
statuses["executed"] = 3

from .Base import Base
from .DiscordAccount import DiscordAccount
from .SteamAccount import SteamAccount
from .Player import Player
from .Wipe import Wipe
from .Status import Status
from .Item import Item
from .NumberedItem import NumberedItem
from .ClaimItem import ClaimItem
from .Claim import Claim


from sqlalchemy import func, select

async def models_init():
    global engine
    global async_session

    engine = create_async_engine(main_config["sql_connection_row"], echo=True, connect_args=main_config["connect_args"])
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        async with session.begin():
            row_count = (await session.execute(select(func.count(Status.id)))).scalar()
            if row_count < 3:
                print("Инициализация таблицы Status")
                session.add(Status(name="not_approved"))
                session.add(Status(name="approved"))
                session.add(Status(name="executed"))
                if (await session.execute(select(func.count(Wipe.id)))).scalar() == 0:
                    session.add(Wipe())

    return async_session

