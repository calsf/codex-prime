#INVASION COMMANDS:
# !invasions

import discord
from discord.ext import commands
import asyncio
from src import sess


class Invasions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Ready')
        # Periodically check

    @commands.command()
    async def invasions(self, ctx):
        inv = await sess.request('invasions')
        print(inv)


def setup(bot):
    bot.add_cog(Invasions(bot))
