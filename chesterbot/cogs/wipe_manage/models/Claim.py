from datetime import datetime
from typing import List, Optional

from sqlalchemy import Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class Claim(Base):
    __tablename__ = "claim"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    player: Mapped[Optional["Player"]] = relationship("Player", back_populates="claim")

    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"), default=1)
    status: Mapped[Optional["Status"]] = relationship("Status", back_populates="claim")

    wipe_id: Mapped[int] = mapped_column(ForeignKey("wipe.id"))
    wipe: Mapped[Optional["Wipe"]] = relationship("Wipe")

    started: Mapped[int] = mapped_column(DateTime, default=datetime.utcnow)
    approved: Mapped[int] = mapped_column(DateTime, default=datetime.utcnow)
    executed: Mapped[int] = mapped_column(DateTime, default=datetime.utcnow)

    item: Mapped[List["Item"]] = relationship("Item",
        secondary='claim_item', back_populates="claim"
    )

    def __repr__(self) -> str:
        return f"Claim(id={self.id!r}, player_id={self.player_id!r}," + \
            f" status_id={self.status_id!r}, wipe_id={self.wipe_id!r}," + \
            f" started={self.started!r}, approved={self.approved!r}," + \
            f" executed={self.executed!r})"

    @staticmethod
    def get_or_create(session, item, **kwargs):
        with session.begin():
            instance = session.query(Claim).filter_by(**kwargs).first()
            if instance:
                return instance
            else:
                instance = Claim(item=item, **kwargs)
                session.add(instance)
                return instance

