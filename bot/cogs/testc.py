import discord
from discord.ui import *
from discord import app_commands
from discord.ext import commands


class TestC(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.db = self.bot.db

    @app_commands.command(name="test", description="test")
    async def test(self, interaction: discord.Interaction):
        await interaction.response.send_message(content="e")


async def setup(bot):
    await bot.add_cog(TestC(bot))
