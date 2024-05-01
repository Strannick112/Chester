from typing import Optional

from sqlalchemy import select, BigInteger, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class NumberedItem(Base):
    __tablename__ = "numbered_item"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    number: Mapped[str] = mapped_column(BigInteger)

    item_id: Mapped[int] = mapped_column(ForeignKey("item.id"))
    item: Mapped[Optional["Item"]] = relationship("Item", back_populates="numbered_item")

    claim: Mapped[Optional["Claim"]] = relationship("Claim",
        secondary='claim_item', back_populates="numbered_items"
    )

    def __repr__(self) -> str:
        return f"NumberedItems(id={str(self.id)!r}, number={str(self.number)!r}, item_id={str(self.item_id)!r})"

    @staticmethod
    async def get_or_create(session, number, item_id):
        instance = (
            await session.execute(select(NumberedItem).filter_by(number=number, item_id=item_id))
        ).scalars().first()
        if not instance:
            instance = NumberedItem(number=number, item_id=item_id)
            session.add(instance)
            # await session.flush()
        return instance
