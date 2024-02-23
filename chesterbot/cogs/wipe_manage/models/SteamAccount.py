from typing import Optional

from sqlalchemy import String, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class SteamAccount(Base):
    __tablename__ = "steam_account"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    ku_id: Mapped[str] = mapped_column(String(100))
    nickname: Mapped[str] = mapped_column(String(100))

    player: Mapped[Optional["Player"]] = relationship("Player")

    def __repr__(self) -> str:
        return f"SteamAccount(id={str(self.id)!r}, ku_id={str(self.ku_id)!r}, nickname={str(self.nickname)!r})"


    @staticmethod
    def get_or_create(session, ku_id, nickname):
        # with session.begin():
        instance = session.query(SteamAccount).filter_by(ku_id=ku_id).first()
        # instance = session.execute(select(SteamAccount).where(SteamAccount.ku_id == ku_id)).first()[0]
        if instance:
            if nickname != instance.nickname:
                instance.nickname = nickname
        else:
            instance = SteamAccount(ku_id=ku_id, nickname=nickname)
            session.add(instance)
        # session.close()
        return instance
