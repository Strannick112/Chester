from typing import Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class SteamAccount(Base):
    __tablename__ = "steam_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ku_id: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str] = mapped_column(String(100))

    player: Mapped[Optional["Player"]] = relationship("Player")

    def __repr__(self) -> str:
        return f"SteamAccount(id={self.id!r}, ku_id={self.ku_id!r}, nickname={self.nickname!r})"

    @staticmethod
    def get_or_create(session, **kwargs):
        with session.begin():
            instance = session.query(SteamAccount).filter_by(**kwargs).first()
            if instance:
                return instance
            else:
                instance = SteamAccount(**kwargs)
                session.add(instance)
                return instance
