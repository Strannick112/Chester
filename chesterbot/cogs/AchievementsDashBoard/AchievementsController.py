import asyncio
import codecs
import io
import json
import os

import discord
from discord.ext import tasks, commands
from sqlalchemy import select

from chesterbot import main_config, models
from chesterbot.cogs.AchievementsDashBoard.AchievementsReader import AchievementsReader
from chesterbot.cogs.AchievementsDashBoard.AchievementsView import AchievementsView
from chesterbot.models import SteamAccount
from chesterbot.models.WipeAchievements import WipeAchievements


class AchievementsController(commands.Cog, name="Доска статистики"):
    def __init__(self, bot):
        self.chester_bot = bot
        self.channel = None
        self.message = None
        self.message_id = None
        self.reader = AchievementsReader(self.chester_bot)
        self.view = AchievementsView(self.chester_bot)

    async def on_ready(self):
        self.channel = self.chester_bot.get_channel(main_config["achievements_channel"])
        if not os.path.exists("./chesterbot/cogs/achievements"):
            os.mkdir("./chesterbot/cogs/achievements")
        if not os.path.exists(f"./chesterbot/cogs/achievements/message.json"):
            with codecs.open(f"./chesterbot/cogs/achievements/message.json", "w", encoding="utf-8") as file:
                json.dump(0, file)

        with codecs.open(f"./chesterbot/cogs/achievements/message.json", "rb", encoding="utf-8") as file:
            self.message_id = json.load(file)

        try:
            self.message = await self.channel.fetch_message(self.message_id)
        except:
            try:
                embed_picture = discord.File(main_config["achievement_embed_picture"])
            except OSError:
                return
            await self.channel.send(file=embed_picture)
            embed = discord.Embed(
                title="Статистика",
                description="Доска создана, начат сбор информации...",
                colour=discord.Colour.dark_teal()
            )
            self.message = await self.channel.send(embeds=[embed])
            self.message_id = self.message.id
            with codecs.open(f"./chesterbot/cogs/achievements/message.json", "w", encoding="utf-8") as file:
                json.dump(self.message_id, file)
        self.reload_data.start()

    @tasks.loop(minutes=1)
    async def reload_data(self):
        try:
            await self.reader.update_players_points()
            await self.save_achievements_info()
            await self.message.edit(**(await self.view.update()))
        except Exception as error:
            print(error)

    @commands.command(name=main_config['short_server_name'] + "_get_achievements_info")
    @commands.has_role(main_config['master_role'])
    async def get_achievements_info(self, ctx, ku_id: str):
        """
            Отображает полную статистику игрока, сколько баллов и за что выдано для доски рейтинга:
            ku_id - уникальный klei_id игрока в игре
        """
        reader = self.model.reader
        raw_stat_info = await reader.get_player_raw_info(reader.get_player_saves(key = lambda x: x == ku_id)[0][1])
        stat = reader.get_player_stat(raw_stat_info)
        text_message = f"""Подробная информация об игроке "{ku_id}":
        Количество очков: {reader.calculate_points(stat)}
        ```json
        {stat} 
        ```"""
        if len(text_message) < 4000:
            await ctx.send(stat)
        else:
            updated_stat = json.dumps(
                {
                    "title": f"""Подробная информация об игроке "{ku_id}" """,
                    "Количество очков": reader.calculate_points(stat),
                    **stat
                }, indent=2, ensure_ascii=False
            )

            await ctx.send(file = discord.File(fp=io.BytesIO(updated_stat.encode('utf-8')), filename=f"{ku_id}.json"))

    @commands.command(name=main_config['short_server_name'] + "_save_achievements")
    @commands.has_role(main_config['master_role'])
    async def save_achievements_wipe_info(self, ctx):
        """
            Сохраняет рейтинг игроков на текущий вайп
        """
        await self.save_achievements_info()
        await ctx.reply(self.__replies['achievements_save_success'])
        return True

    async def save_achievements_info(self):
        async with self.chester_bot.async_session() as session:
            async with session.begin():
                last_wipe_id = (await session.execute(select(models.Wipe).order_by(
                    models.Wipe.id.desc()))).scalars().first().id
                for player in await self.reader.player_points:
                    try:
                        await WipeAchievements.create_or_update(
                            session=session,
                            steam_account_id=(await SteamAccount.get_by_ku_id(session=session, ku_id=player["ku_id"])).id,
                            wipe_id=last_wipe_id, score=player["Очки"]
                        )
                    except Exception as error:
                        print(error)
