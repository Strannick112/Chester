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

    claim: Mapped[List["Claim"]] = relationship("Claim", back_populates="wipe")

    def __repr__(self) -> str:
        return f"Wipe(id={str(self.id)!r}, started={str(self.started)!r}, stopped={str(self.stopped)!r})"

    @staticmethod
    def get_or_create(session, **kwargs):
        # with session.begin():
        instance = session.query(Wipe).filter_by(**kwargs).first()
        if instance:
            pass
        else:
            instance = Wipe(**kwargs)
            session.add(instance)
        # session.close()
        return instance
