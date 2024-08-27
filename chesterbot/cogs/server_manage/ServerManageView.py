import discord
from discord import ButtonStyle, Interaction
from discord.ui import View

from chesterbot import main_config
from chesterbot.cogs.server_manage.commands import restart, stop, soft_stop, soft_restart, soft_world_regenerate


class ServerManageView(View):

    def __init__(self, bot):
        self.chester_bot = bot
        super().__init__()

    @discord.ui.button(label="Запуск сервера", style=ButtonStyle.green, row=0)
    async def start_callback(self, interaction, button):
        await restart()
        await interaction.response.send_message("Запуск сервера принят к исполнению")

    @discord.ui.button(label="Перезапуск сервера", style=ButtonStyle.green, row=0)
    async def restart_callback(self, interaction, button):
        await restart()
        await interaction.response.send_message("Перезагрузка сервера принята к исполнению")

    @discord.ui.button(label="Перезапуск сервера через 1 минуту", style=ButtonStyle.green, row=0)
    async def soft_restart_callback(self, interaction, button):
        await soft_restart()
        await interaction.response.send_message("Перезагрузка сервера через 1 минуту принята к исполнению")

    @discord.ui.button(label="Остановка сервера", style=ButtonStyle.red, row=1)
    async def stop_callback(self, interaction, button):
        await stop()
        await interaction.response.send_message("Остановка сервера принята к исполнению")

    @discord.ui.button(label="Остановка сервера через 1 минуту", style=ButtonStyle.red, row=1)
    async def soft_stop_callback(self, interaction, button):
        await soft_stop()
        await interaction.response.send_message("Остановка сервера через 1 минуту принята к исполнению")

    @discord.ui.button(label="Пересоздание игрового мира", style=ButtonStyle.red, row=1)
    async def soft_world_regenerate_callback(self, interaction, button):
        await soft_world_regenerate()
        await interaction.response.send_message("Пересоздание игрового мира принято к исполнению")

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        if interaction.user.get_role(main_config["master_role"]) is not None:
            return True
        else:
            return False
