from datetime import datetime
from typing import List

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class Wipe(Base):
    __tablename__ = "wipe"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    started: Mapped[int] = mapped_column(DateTime(timezone=True), default=func.now())
    stopped: Mapped[int] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())

    claims: Mapped[List["Claim"]] = relationship("Claim", back_populates="wipe")

    def __repr__(self) -> str:
        return f"Wipe(id={str(self.id)!r}, started={str(self.started)!r}, stopped={str(self.stopped)!r})"

    def __str__(self):
        claims = "[\n"
        for index, claim in enumerate(self.claims):
            claims += f"ᅠᅠ{index + 1}. <@" + str(claim.player.discord_account.discord_id) + ">ᅠᅠ"
            claims += claim.message_link
            claims += ";\n"
        claims += "]"
        stopped = '?' if self.stopped == self.started else str(self.stopped)
        return (f"id={str(self.id)},\nstarted={str(self.started)},\nstopped={stopped!r},\n"
                f"claims={str(claims)}\n")

    @staticmethod
    def get_or_create(session, **kwargs):
        instance = session.query(Wipe).filter_by(**kwargs).first()
        if instance:
            pass
        else:
            instance = Wipe(**kwargs)
            session.add(instance)
        return instance
