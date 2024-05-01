import asyncio
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, func, BigInteger, String, select, update
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
        )

    @staticmethod
    async def get_or_create(*, session, numbered_items, revoke, player_id, **kwargs):
        query = select(Claim).filter_by(**kwargs, player_id=player_id)
        result = await session.execute(query)
        claim = result.scalars().first()
        if claim:
            return claim
        try:
            session.expunge(claim)
        except:
            pass
        old_claim = await revoke(player_id, session)
        if old_claim:
            print("How Rare!!!")
            await session.execute(
                update(Claim)
                .where(Claim.player_id == player_id)
                .values(
                    message_id=kwargs.get("message_id"),
                    channel_id=kwargs.get("channel_id"),
                    message_link=kwargs.get("message_link"),
                    status_id=statuses.get("not_approved")
                )
            )
            old_claim.numbered_items.clear()
            old_claim.numbered_items = numbered_items
            session.add(old_claim)  # Добавляем только если нужно сохранять изменения
            return old_claim
        try:
            session.expunge(old_claim)
        except:
            pass
        new_claim = Claim(player_id=player_id, **kwargs)
        print(numbered_items)
        new_claim.numbered_items.clear()
        for numbered_item in numbered_items:
            new_claim.numbered_items.append(numbered_item)
        print(new_claim.numbered_items)
        session.add(new_claim)
        return new_claim

    semaphore_give_items = asyncio.Semaphore(1)

    async def give_items(self, *, session, console_dst_checker: ConsoleDSTChecker) -> bool:
        async with self.semaphore_give_items:
            await session.refresh(self)
            if self.status_id == statuses.get("approved"):
                self.executed = func.now()
                self.status_id = statuses.get("executed")
                session.add(self)
                ku_id = (await (await self.awaitable_attrs.player).awaitable_attrs.steam_account).ku_id
                tasks = []
                for world in main_config["worlds"]:
                    for numbered_item in await self.awaitable_attrs.numbered_items:
                        item_id = shlex.quote(
                            (await numbered_item.awaitable_attrs.item).console_id
                        )
                        command = f"""LookupPlayerInstByUserID(\\\"{ku_id}\\\").components.inventory:""" \
                            f"""GiveItem(SpawnPrefab(\\\"{item_id}\\\"))"""
                        tasks.append(
                            asyncio.create_task(
                                console_dst_checker.check(
                                    command,
                                    r'\[string "LookupPlayerInstByUserID\("(' +
                                    ku_id +
                                    r')"\)[\w\W]*?\.\.\."\]\:1\: attempt to index a nil value',
                                    world["shard_id"], world["screen_name"], "is_normal", 5
                                )
                            )
                        )
                for task in asyncio.as_completed(tasks):
                    result = await task
                    if result == ku_id:
                        await session.commit()
                        return True
                await session.rollback()
                return False

    async def check_days(self, *, console_dst_checker: ConsoleDSTChecker):
        ku_id = (await (await self.awaitable_attrs.player).awaitable_attrs.steam_account).ku_id
        raw_results = set()
        for world in main_config["worlds"]:
            command = f"""print('CheckDaysForPlayer: ', \\\"{ku_id}\\\", TheNet:GetClientTableForUser(\\\"{ku_id}\\\").playerage)"""
            raw_results.add(
                await console_dst_checker.check(
                    command,
                    r'CheckDaysForPlayer:\s+' + ku_id + r'\s+([\d]+)',
                    world["shard_id"], world["screen_name"], "0", 5
                )
            )
        for result in raw_results:
            if int(result) > 0:
                return int(result)
        return 0

    semaphore_rollback_claim = asyncio.Semaphore(1)

    async def rollback_claim(self, *, session) -> bool:
        async with self.semaphore_rollback_claim:
            await session.refresh(self)
            if self.status_id == statuses.get("executed"):
                self.executed = self.started
                self.status_id = statuses.get("approved")
                session.add(self)
                return True
            else:
                return False

    semaphore_approve = asyncio.Semaphore(1)

    async def approve(self, *, session) -> bool:
        async with self.semaphore_approve:
            await session.refresh(self)
            if self.status_id == statuses.get("not_approved"):
                self.approved = func.now()
                self.status_id = statuses.get("approved")
                print("APPROVE_3")
                session.add(self)
                print("APPROVE_4")
                return True
            else:
                return False

    async def get_discord_id(self):
        return (await (await self.awaitable_attrs.player).awaitable_attrs.discord_account).discord_id

    async def get_steam_nickname(self):
        return (await (await self.awaitable_attrs.player).awaitable_attrs.steam_account).nickname
