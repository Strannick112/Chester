from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class Status(Base):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    claim: Mapped[List["Claim"]] = relationship("Claim")

    def __repr__(self) -> str:
        return f"Status(id={self.id!r}, name={self.name!r})"

    @staticmethod
    def get_or_create(session, **kwargs):
        with session.begin():
            instance = session.query(Status).filter_by(**kwargs).first()
            if instance:
                return instance
            else:
                instance = Status(**kwargs)
                session.add(instance)
                return instance
