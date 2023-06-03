import discord
from discord import ButtonStyle, Interaction
from discord.ui import View

from chesterbot import main_config
from chesterbot.cogs.server_manage import stop, soft_stop, restart, soft_restart


class ServerManageView(View):
    @discord.ui.button(label="Запуск сервера", style=ButtonStyle.green)
    async def start_callback(self, interaction):
        await interaction.response.send_message("Запуск сервера принят к исполнению")
        return await restart()

    @discord.ui.button(label="Остановка сервера", style=ButtonStyle.red)
    async def stop_callback(self, interaction):
        await interaction.response.send_message("Остановка сервера принята к исполнению")
        return await stop()

    @discord.ui.button(label="Остановка сервера через 1 минуту", style=ButtonStyle.red)
    async def soft_stop_callback(self, interaction):
        await interaction.response.send_message("Остановка сервера через 1 минуту принята к исполнению")
        return await soft_stop()

    @discord.ui.button(label="Перезапуск сервера", style=ButtonStyle.green)
    async def restart_callback(self, interaction):
        await interaction.response.send_message("Перезагрузка сервера принята к исполнению")
        return await restart()

    @discord.ui.button(label="Перезапуск сервера через 1 минуту", style=ButtonStyle.green)
    async def soft_restart_callback(self, interaction):
        await interaction.response.send_message("Перезагрузка сервера через 1 минуту принята к исполнению")
        return await soft_restart()

    async def interaction_check(self, interaction: Interaction, /) -> bool:
        for role in interaction.user.roles:
            if role.__str__() == main_config['master_role']:
                return True
        else:
            return False
