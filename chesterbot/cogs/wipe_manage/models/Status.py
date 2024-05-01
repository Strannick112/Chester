from typing import List

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class Status(Base):
    __tablename__ = "status"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100))
    claim: Mapped[List["Claim"]] = relationship("Claim")

    def __repr__(self) -> str:
        return f"Status(id={str(self.id)!r}, name={str(self.name)!r})"

    @staticmethod
    async def get_or_create(session, **kwargs):
        instance = (await session.execute(select(Status).filter_by(**kwargs))).scalars().first()
        if instance:
            pass
        else:
            instance = Status(**kwargs)
            session.add(instance)
            # await session.flush()
        return instance
