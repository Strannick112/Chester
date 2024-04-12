from typing import Optional

from sqlalchemy import String, select, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    console_id: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

    numbered_item: Mapped[Optional["NumberedItem"]] = relationship("NumberedItem")

    def __repr__(self) -> str:
        return f"Item(id={str(self.id)!r}, console_id={str(self.console_id)!r}, name={str(self.name)!r})"

    @staticmethod
    async def get_or_create(session, **kwargs):
        instance = (await session.execute(select(Item).filter_by(**kwargs))).scalars().first()
        if not instance:
            instance = Item(**kwargs)
            session.add(instance)
            await session.flush()
        return instance
