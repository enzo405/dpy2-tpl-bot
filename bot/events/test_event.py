import discord

from bot.database import db, TableName


class Test:
    def __init__(self, bot: discord.Client):
        self.bot = bot
