from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class DiscordAccount(Base):
    __tablename__ = "discord_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    discord_id: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str] = mapped_column(String(100))

    player: Mapped[Optional["Player"]] = relationship("Player")

    def __repr__(self) -> str:
        return f"DiscordAccount(id={self.id!r}, discord_id={self.discord_id!r}, nickname={self.nickname!r})"

    @staticmethod
    def get_or_create(session, **kwargs):
        with session.begin():
            instance = session.query(DiscordAccount).filter_by(**kwargs).first()
            if instance:
                return instance
            else:
                instance = DiscordAccount(**kwargs)
                session.add(instance)
                return instance
