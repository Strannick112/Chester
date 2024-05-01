from sqlalchemy import ForeignKey, select, Table, Column
from sqlalchemy.orm import Mapped, mapped_column

from .Base import Base


class ClaimItem(Base):
    __tablename__ = "claim_item"

    # id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    claim_id: Mapped[int] = mapped_column(ForeignKey("claim.id"), primary_key=True)
    numbered_item_id: Mapped[int] = mapped_column(ForeignKey("numbered_item.id"), primary_key=True)

    def __repr__(self) -> str:
        return f"ClaimItem(id={str(self.id)!r}, claim_id={str(self.claim_id)!r}, numbered_item_id={str(self.numbered_item_id)!r})"

    @staticmethod
    async def get_or_create(session, **kwargs):
        instance = (await session.execute(select(ClaimItem).filter_by(**kwargs))).scalars().first()
        if instance:
            pass
        else:
            instance = ClaimItem(**kwargs)
            session.add(instance)
        await session.flush()
        return instance

# claim_item = Table(
#     "claim_item",
#     Base.metadata,
#     Column("claim_id", ForeignKey("claim.id"), primary_key=True),
#     Column("numbered_item_id", ForeignKey("numbered_item.id"), primary_key=True),
# )
