import asyncio

import chester_bot
from chester_bot.config import main_config


async def main():
    await chester_bot.bot.add_cog(chester_bot.bot_commands.server_manage.ServerManage(chester_bot.bot))
    await chester_bot.bot.add_cog(chester_bot.bot_commands.bot_manage.BotManage(chester_bot.bot))
    await chester_bot.bot.add_cog(chester_bot.bot_commands.wipe_manage.WipeManage(chester_bot.bot))
    # await chester_bot.bot.load_extension(name="chester_bot.bot_commands.server_manage", package="server_manage")
    await chester_bot.bot.start(main_config['token'])

asyncio.run(main())
