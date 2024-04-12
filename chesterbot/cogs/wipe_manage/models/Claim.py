from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, func, BigInteger, String, select, update
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session

from chesterbot import main_config
from chesterbot.ConsoleDSTChecker import ConsoleDSTChecker
from . import Status, statuses
from .Base import Base

import re
import shlex


class Claim(Base):
    __tablename__ = "claim"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    message_id: Mapped[int] = mapped_column(BigInteger)
    message_link: Mapped[str] = mapped_column(String(100))
    channel_id: Mapped[int] = mapped_column(BigInteger)

    player_id: Mapped[int] = mapped_column(ForeignKey("player.id"))
    player: Mapped[Optional["Player"]] = relationship("Player", back_populates="claim")

    status_id: Mapped[int] = mapped_column(ForeignKey("status.id"), default=1)
    status: Mapped[Optional["Status"]] = relationship("Status", back_populates="claim")

    wipe_id: Mapped[int] = mapped_column(ForeignKey("wipe.id"))
    wipe: Mapped[Optional["Wipe"]] = relationship("Wipe")

    started: Mapped[int] = mapped_column(DateTime, default=func.now())
    approved: Mapped[int] = mapped_column(DateTime, default=func.now())
    executed: Mapped[int] = mapped_column(DateTime, default=func.now())

    numbered_items: Mapped[List["NumberedItem"]] = relationship("NumberedItem",
        secondary='claim_item', back_populates="claim"
    )

    def __repr__(self) -> str:
        return f"Claim(id={str(self.id)!r}, message_id={str(self.message_id)}," + \
                f"channel_id={str(self.channel_id)}, player_id={str(self.player_id)!r}," + \
                f" status_id={str(self.status_id)!r}, wipe_id={str(self.wipe_id)!r}," + \
                f" started={str(self.started)!r}, approved={str(self.approved)!r}," + \
                f" executed={str(self.executed)!r}, message_link={str(self.message_link)})"

    async def to_str(self):
        items = "[\n"
        for numbered_item in await self.awaitable_attrs.numbered_items:
            item = await numbered_item.awaitable_attrs.item
            items += f'ᅠᅠ{numbered_item.number + 1}. ' + {'console_id': item.console_id, 'name': item.name}.__str__() + ',\n'
        items += "]"
        approved = '?' if self.approved == self.started else str(self.approved)
        executed = '?' if self.executed == self.started else str(self.executed)
        return (
            f"id игрока={str(self.player_id)},\n"
            f"Дискорд аккаунт={'<@' + str((await(await self.awaitable_attrs.player).awaitable_attrs.discord_account).discord_id) + '>'},\n"
            f"Идентификатор={str((await(await self.awaitable_attrs.player).awaitable_attrs.steam_account).ku_id)!r},\n"
            f"Игровой ник={str((await (await self.awaitable_attrs.player).awaitable_attrs.steam_account).nickname)},\n"
            f"Статус={str((await self.awaitable_attrs.status).name)},\nПредметы={items},\n"
            f"Создана={str(self.started)!r},\nОдобрена={approved!r},\n"
            f"Выполнена={executed!r},\nЗаявка={str(self.message_link)},\n"
            f"ИД канала={self.channel_id!r}\n"
        )

    @staticmethod
    async def get_or_create(*, session, numbered_items, revoke, player_id, **kwargs):
        if instance := (await session.execute(select(Claim).filter_by(**kwargs, player_id=player_id))).scalars().first():
            return instance
        if old_claim := await revoke(player_id, session):
            await session.execute(update(Claim).where(Claim.player_id == player_id).values(
                message_id=kwargs.get("message_id"),
                channel_id=kwargs.get("channel_id"),
                message_link=kwargs.get("message_link"),
                status_id=statuses.get("not_approved"),
            ))
            (await old_claim.awaitable_attrs.numbered_items).clear()
            session.add(old_claim)
            await session.flush()
            old_claim.numbered_items = numbered_items
            session.add(old_claim)
            await session.flush()
            return old_claim
        instance = Claim(numbered_items=numbered_items, player_id=player_id, **kwargs)
        session.add(instance)
        await session.flush()
        return instance

    async def give_items(self, *, session, console_dst_checker: ConsoleDSTChecker) -> bool:
        with Session() as sess:
            if self.status_id == statuses.get("approved"):
                for world in main_config["worlds"]:
                    for numbered_item in await self.awaitable_attrs.numbered_items:
                        item = await numbered_item.awaitable_attrs.item
                        dst_nickname = re.sub(
                            r'\'', r"\\\\\'",
                            (await (await self.awaitable_attrs.player).awaitable_attrs.steam_account).nickname
                        )
                        dst_nickname = re.sub(r'\"', r"\\\\\"", dst_nickname)
                        item_id = shlex.quote(item.console_id)
                        command = f"""screen -S {world["screen_name"]} -X stuff"""\
                            f""" "UserToPlayer(\\\"{dst_nickname}\\\").components.inventory:"""\
                            f"""GiveItem(SpawnPrefab(\\\"{item_id}\\\"))\n\""""
                        result = await console_dst_checker.check(
                            command,
                            r'\[string "UserToPlayer\("(' +
                            dst_nickname +
                            r')"\)[\w\W]*?\.\.\."\]\:1\: attempt to index a nil value',
                            world["shard_id"], world["screen_name"], "is_normal", 5
                            )
                        if result == dst_nickname:
                            break
                    else:
                        self.executed = func.now()
                        self.status_id = statuses.get("executed")
                        sess.add(self)
                        sess.commit()
                        return True
            sess.rollback()
            return False

    async def check_days(self, *, console_dst_checker: ConsoleDSTChecker):
        dst_nickname = re.sub(r'\'', r"\\\\\'", (await (await self.awaitable_attrs.player).awaitable_attrs.steam_account).nickname)
        dst_nickname = re.sub(r'\"', r"\\\\\"", dst_nickname)
        raw_results = set()
        for world in main_config["worlds"]:
            command = f"""screen -S {world["screen_name"]} -X stuff""" \
                      f""" "for k,v in pairs(AllPlayers) do print('CheckDaysForPlayer: ', v.name, TheNet:GetClientTableForUser(v.userid).playerage) end\n\""""
            raw_results.add(
                await console_dst_checker.check(
                    command,
                    r'CheckDaysForPlayer:\s+' + dst_nickname + r'\s+([\d]+)',
                    world["shard_id"], world["screen_name"], "0", 5
                )
            )
        for result in raw_results:
            if int(result) > 0:
                return int(result)
        return 0

    # В РАЗРАБОТКЕ!!!
    # async def check_items(self, console_dst_checker: ConsoleDSTChecker, is_ok: int):
    #     dst_nickname = re.sub(r'\'', r"\\\\\'", self.player.steam_account.nickname)
    #     dst_nickname = re.sub(r'\"', r"\\\\\"", dst_nickname)
    #     raw_results = dict()
    #     for world in main_config["worlds"]:
    #         raw_results[world["shard_id"]] = []
    #         for item in self.items:
    #             command = f"""screen -S {world["screen_name"]} -X stuff""" \
    #                       f""" "for k,v in pairs(AllPlayers) do print('CheckDaysForPlayer: ', v.name, TheNet:GetClientTableForUser(v.userid).playerage) end\n\""""
    #             raw_results[world["shard_id"]].append(
    #                 await console_dst_checker.check(
    #                     command,
    #                     r'CheckDaysForPlayer:\s+' + dst_nickname + r'\s+([\d]+)',
    #                     world["shard_id"], world["screen_name"], "0", 5
    #                 )
    #             )
    #     for result in raw_results:
    #         if int(result) > 0:
    #             return int(result) > is_ok
    #     return False

    async def rollback_claim(self, *, session) -> bool:
        if self.status_id == statuses.get("executed"):
            self.executed = self.started
            self.status_id = statuses.get("approved")
            session.add(self)
            return True
        else:
            return False

    async def approve(self, *, session) -> bool:
        if self.status_id == statuses.get("not_approved"):
            self.approved = func.now()
            self.status_id = statuses.get("approved")
            print("APPROVE_3")
            session.add(self)
            print("APPROVE_4")
            return True
        else:
            return False
