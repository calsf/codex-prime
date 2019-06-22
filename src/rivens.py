# RIVEN COMMANDS:
# !riven <"weapon">

import discord
from discord.ext import commands
from src import sess


class Rivens(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # Quotations required for accurate results, example: !riven "Twin Rogga"
    @commands.command()
    async def riven(self, ctx, riven=''):
        riv = await sess.request(f'rivens/search/{riven}')

        # Iterate through the dictionary of returned rivens, only return if exact match is found
        for key, value in riv.items():
            if value['rerolled']['compatibility'].lower() == riven.lower():
                embed = discord.Embed(title=f'{value["rerolled"]["compatibility"]} Riven')
                embed.add_field(name='Average Price (Unrolled)', value=str(int(value["unrolled"]["avg"])),
                                inline=False)
                embed.add_field(name='Median Price (Unrolled)', value=str(int(value["unrolled"]["median"])),
                                inline=False)
                embed.add_field(name='Average Price (Rerolled)', value=str(int(value["rerolled"]["avg"])),
                                inline=False)
                embed.add_field(name='Median Price (Rerolled)', value=str(int(value["rerolled"]["median"])),
                                inline=False)
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Rivens(bot))
