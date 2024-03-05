from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session

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
from .ClaimItem import ClaimItem
from .Claim import Claim


from sqlalchemy import create_engine, func

engine = create_engine("sqlite:///dst_keriwell", echo=True)
Base.metadata.create_all(engine)

# session = Session(engine)
# session.autobegin = False
#
# # with session.begin():
# #     row_count = session.query(func.count(Status.id)).scalar()
# #     if row_count < 3:
# #         print("Инициализация таблицы Status")
# #         session.add(Status(name="not_approved"))
# #         session.add(Status(name="approved"))
# #         session.add(Status(name="executed"))
#
# with session.begin():
#     if session.query(func.count(Wipe.id)).scalar() == 0:
#         session.add(Wipe())

engine = None
async_session = None

async def models_init() -> None:
    global engine
    global async_session

    engine = create_async_engine(
        "postgresql+asyncpg://scott:tiger@localhost/test",
        echo=True,
    )

    # async_sessionmaker: a factory for new AsyncSession objects.
    # expire_on_commit - don't expire objects after transaction commit
    async_session = async_sessionmaker(engine, expire_on_commit=False)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with async_session() as session:
        row_count = session.query(func.count(Status.id)).scalar()
        if row_count < 3:
            print("Инициализация таблицы Status")
            session.add(Status(name="not_approved"))
            session.add(Status(name="approved"))
            session.add(Status(name="executed"))
            if session.query(func.count(Wipe.id)).scalar() == 0:
                session.add(Wipe())

    # for AsyncEngine created in function scope, close and
    # clean-up pooled connections
    # await engine.dispose()