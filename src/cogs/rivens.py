# RIVEN COMMANDS:
# !riven <weapon>

import discord
from discord.ext import commands
from src import sess


class Rivens(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def riven(self, ctx, *, riven=''):
        riv = await sess.request(f'rivens/search/{riven}')
        if riv is 0:
            print("Could not retrieve data.")
            return

        # Iterate through the dictionary of returned rivens, only return if exact match is found
        for key, value in riv.items():
            # Check if unrolled information available
            if value['unrolled'] is None:
                unroll_avg = "No Information Available."
                unroll_med = "No Information Available."
            else:
                unroll_avg = str(value["unrolled"]["avg"])
                unroll_med = str(value["unrolled"]["median"])
                riv_name = value['unrolled']['compatibility'].lower()

            # Check if rerolled information available
            if value['rerolled'] is None:
                reroll_avg = "No Information Available."
                reroll_med = "No Information Available."
            else:
                reroll_avg = str(value["rerolled"]["avg"])
                reroll_med = str(value["rerolled"]["median"])
                riv_name = value['rerolled']['compatibility'].lower()

            # Check riven name from riv.items() with user input
            if riv_name == riven.lower():
                embed = discord.Embed(title=f'{riv_name.title()} Riven')
                embed.add_field(name='Average Price (Unrolled)', value=unroll_avg,
                                inline=False)
                embed.add_field(name='Median Price (Unrolled)', value=unroll_med,
                                inline=False)
                embed.add_field(name='Average Price (Rerolled)', value=reroll_avg,
                                inline=False)
                embed.add_field(name='Median Price (Rerolled)', value=reroll_med,
                                inline=False)
                await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Rivens(bot))
