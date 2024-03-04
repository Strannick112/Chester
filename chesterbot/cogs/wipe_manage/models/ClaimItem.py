from datetime import datetime

from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base


class ClaimItem(Base):
    __tablename__ = "claim_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claim.id"))
    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))

    def __repr__(self) -> str:
        return f"ClaimItem(id={str(self.id)!r}, claim_id={str(self.claim_id)!r}, item_id={str(self.item_id)!r})"

    @staticmethod
    def get_or_create(session, **kwargs):
        instance = session.query(ClaimItem).filter_by(**kwargs).first()
        if instance:
            pass
        else:
            instance = ClaimItem(**kwargs)
            session.add(instance)
        return instance
