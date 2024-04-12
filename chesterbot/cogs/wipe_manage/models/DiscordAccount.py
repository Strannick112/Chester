from typing import Optional

from sqlalchemy import String, Integer, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class DiscordAccount(Base):
    __tablename__ = "discord_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discord_id: Mapped[int] = mapped_column(Integer)
    name: Mapped[str] = mapped_column(String(100))
    display_name: Mapped[str] = mapped_column(String(100))

    player: Mapped[Optional["Player"]] = relationship("Player")

    def __repr__(self) -> str:
        return f"DiscordAccount(id={str(self.id)!r}, discord_id={str(self.discord_id)!r}, name={str(self.name)!r}, display_name={str(self.display_name)!r})"

    @staticmethod
    async def get_or_create(session, discord_id, name, display_name):
        instance = (await session.execute(select(DiscordAccount).filter_by(discord_id=discord_id))).scalars().first()
        if instance:
            if name != instance.name:
                instance.name = name
            if display_name != instance.display_name:
                instance.display_name = display_name
            session.add(instance)
        else:
            instance = DiscordAccount(discord_id=discord_id, name=name, display_name=display_name)
            session.add(instance)
        await session.flush()
        return instance
