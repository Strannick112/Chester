from typing import List

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class Item(Base):
    __tablename__ = "item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    console_id: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))

    claim: Mapped[List["Claim"]] = relationship("Claim",
        secondary='claim_item', back_populates="item"
    )

    def __repr__(self) -> str:
        return f"Item(id={str(self.id)!r}, console_id={str(self.console_id)!r}, name={str(self.name)!r})"

    @staticmethod
    def get_or_create(session, **kwargs):
        # with session.begin():
        instance = session.query(Item).filter_by(**kwargs).first()
        if instance:
            pass
        else:
            instance = Item(**kwargs)
            session.add(instance)
        # session.close()
        return instance
