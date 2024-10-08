from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from chesterbot import main_config

statuses = dict()
statuses["not_approved"] = 1
statuses["approved"] = 2
statuses["executed"] = 3
statuses["executing"] = 4

engine = None
async_session = None

from .Base import Base
from .DiscordAccount import DiscordAccount
from .SteamAccount import SteamAccount
from .Player import Player
from .Wipe import Wipe
from .Status import Status
from .Item import Item
from .ClaimItem import ClaimItem
from .NumberedItem import NumberedItem
from .Claim import Claim


from sqlalchemy import func, select


async def models_init():
    globals()["engine"] = create_async_engine(main_config["sql_connection_row"], echo=False, connect_args=main_config["connect_args"])
    globals()["async_session"] = async_sessionmaker(globals()["engine"], class_=AsyncSession, expire_on_commit=False)

    async with globals()["engine"].begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with globals()["async_session"]() as session:
        async with session.begin():
            row_count = (await session.execute(select(func.count(Status.id)))).scalar()
            if row_count < 4:
                print("Инициализация таблицы Status")
                session.add(await Status.get_or_create(session=session, name="not_approved"))
                session.add(await Status.get_or_create(session=session, name="approved"))
                session.add(await Status.get_or_create(session=session, name="executed"))
                session.add(await Status.get_or_create(session=session, name="executing"))
                if (await session.execute(select(func.count(Wipe.id)))).scalar() == 0:
                    session.add(Wipe())
                await session.flush()

    return globals()["async_session"]

