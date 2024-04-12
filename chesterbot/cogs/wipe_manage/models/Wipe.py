from datetime import datetime
from typing import List

from sqlalchemy import DateTime, func, select, Integer
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

    # def __str__(self):
    #     claims = "[\n"
    #     for index, claim in enumerate(self.claims):
    #         claims += f"ᅠᅠ{index + 1}. <@" + str(claim.player.discord_account.discord_id) + ">ᅠᅠ"
    #         claims += claim.message_link
    #         claims += ";\n"
    #     claims += "]"
    #     stopped = '?' if self.stopped == self.started else str(self.stopped)
    #     return (f"Номер вайпа={str(self.id)},\nНачало={str(self.started)},\nКонец={stopped!r},\n"
    #             f"Заявки={str(claims)}\n")

    async def to_str(self):
        claims = "[\n"
        for index, claim in enumerate(await self.awaitable_attrs.claims):
            claims += f"ᅠᅠ{index + 1}. <@" + str(
                (
                    await (await claim.awaitable_attrs.player).awaitable_attrs.discord_account
                ).discord_id) + ">ᅠᅠ"
            claims += claim.message_link
            claims += ";\n"
        claims += "]"
        stopped = '?' if self.stopped == self.started else str(self.stopped)
        return (f"Номер вайпа={str(self.id)},\nНачало={str(self.started)},\nКонец={stopped!r},\n"
                f"Заявки={str(claims)}\n")

    @staticmethod
    async def get_or_create(session, **kwargs):
        instance = (await session.execute(select(Wipe).filter_by(**kwargs))).scalars().first()
        if instance:
            pass
        else:
            instance = Wipe(**kwargs)
            session.add(instance)
            await session.flush()
        return instance
