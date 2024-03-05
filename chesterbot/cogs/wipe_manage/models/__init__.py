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

session = Session(engine)
session.autobegin = False

with session.begin():
    row_count = session.query(func.count(Status.id)).scalar()
    if row_count < 3:
        print("Инициализация таблицы Status")
        session.add(Status(name="not_approved"))
        session.add(Status(name="approved"))
        session.add(Status(name="executed"))

with session.begin():
    if session.query(func.count(Wipe.id)).scalar() == 0:
        session.add(Wipe())
