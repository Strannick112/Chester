from typing import List, Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class Player(Base):
    __tablename__ = "player"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    steam_account_id: Mapped[int] = mapped_column(ForeignKey("steam_account.id"))
    steam_account: Mapped[Optional["SteamAccount"]] = relationship("SteamAccount", back_populates="player")

    discord_account_id: Mapped[int] = mapped_column(ForeignKey("discord_account.id"))
    discord_account: Mapped[Optional["DiscordAccount"]] = relationship("DiscordAccount", back_populates="player")

    claim: Mapped[List["Claim"]] = relationship("Claim")

    def __repr__(self) -> str:
        return f"Player(id={str(self.id)!r}, steam_account_id={str(self.steam_account_id)!r}, discord_account_id={str(self.discord_account_id)!r})"

    @staticmethod
    def get_or_create(session, **kwargs):
        # with session.begin():
        instance = session.query(Player).filter_by(**kwargs).first()
        if instance:
            pass
        else:
            instance = Player(**kwargs)
            session.add(instance)
        # session.close()
        return instance
