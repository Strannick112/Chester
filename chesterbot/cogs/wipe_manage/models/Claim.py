import re
from datetime import datetime
from typing import List, Optional

from sqlalchemy import Integer, DateTime, ForeignKey, func, BigInteger, update, String
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

    items: Mapped[List["Item"]] = relationship("Item",
        secondary='claim_item', back_populates="claim"
    )

    def __repr__(self) -> str:
        return f"Claim(id={str(self.id)!r}, message_id={str(self.message_id)}," + \
                f"channel_id={str(self.channel_id)}, player_id={str(self.player_id)!r}," + \
                f" status_id={str(self.status_id)!r}, wipe_id={str(self.wipe_id)!r}," + \
                f" started={str(self.started)!r}, approved={str(self.approved)!r}," + \
                f" executed={str(self.executed)!r}, message_link={str(self.message_link)})"

    def __str__(self):
        items = "[\n"
        for index, item in enumerate(self.items):
            items += f'ᅠᅠ{index}. ' + {'console_id': item.console_id, 'name': item.name}.__str__() + ',\n'
        items += "]"
        approved = '?' if self.approved == self.started else str(self.approved)
        executed = '?' if self.executed == self.started else str(self.executed)
        return (
            f"player\_id={str(self.player_id)},\n"
            f"discord\_user={'<@' + str(self.player.discord_account.discord_id) + '>'},\n"
            f"steam\_account\_ku\_id={str(self.player.steam_account.ku_id)!r},\n"
            f"steam\_account\_nickname={str(self.player.steam_account.nickname)},\n"
            f"status={str(self.status.name)},\nitems={items},\n"
            f"started={str(self.started)!r},\napproved={approved!r},\n"
            f"executed={executed!r},\n message\_link={str(self.message_link)}\n"
        )

    @staticmethod
    async def get_or_create(*, session, items, revoke, player, **kwargs):
        if instance := session.query(Claim).filter_by(**kwargs, player=player).first():
            return instance
        if old_claim := await revoke(player):
            old_claim.message_id = kwargs.get("message_id")
            old_claim.channel_id = kwargs.get("channel_id")
            old_claim.message_link = kwargs.get("message_link")
            old_claim.status_id = statuses.get("not_approved")
            old_claim.items = items
            return old_claim
        instance = Claim(items=items, player=player, **kwargs)
        return instance

    async def give_items(self, *, session, console_dst_checker: ConsoleDSTChecker) -> bool:
        if self.status_id == statuses.get("approved"):
            for world in main_config["worlds"]:
                for item in self.items:
                    dst_nickname = re.sub(r'\'', r"\\\\\'", self.player.dst_nickname)
                    dst_nickname = re.sub(r'\"', r"\\\\\"", dst_nickname)
                    item_id = shlex.quote(item.id)
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
                    self.status = session.query(Status).where(Status.name == "executed").first()
                    return True
        return False

    async def check_days(self, *, console_dst_checker: ConsoleDSTChecker):
        dst_nickname = re.sub(r'\'', r"\\\\\'", self.player.steam_account.nickname)
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

    def rollback_claim(self, *, session) -> bool:
        if self.status_id == statuses.get("executed"):
            self.executed = self.started
            self.status = session.query(Status).where(Status.name == "approved").first()
            return True
        else:
            return False

    def approve(self, *, session) -> bool:
        if self.status == statuses.get("not_approved"):
            self.approved = func.now()
            self.status = session.query(Status).where(Status.name == "approved").first()
            return True
        else:
            return False