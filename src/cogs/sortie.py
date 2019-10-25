# SORTIE COMMANDS:
# !sorties

import discord
from discord.ext import commands
from src import sess


class Sorties(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def sorties(self, ctx):
        sorties = await sess.request('sortie')
        if sorties is 0:
            print("Could not retrieve data.")
            return

        boss = sorties.get('boss')
        faction = sorties.get('faction')
        sortie_list = sorties.get('variants')
        time_left = sorties.get('eta')

        embed = discord.Embed(title=f'Sorties ({time_left} Remaining)', description=f'{boss} ({faction})')
        embed.add_field(name=sortie_list[0]['node'],
                        value=f'Mission: {sortie_list[0]["missionType"]} \n Conditions: {sortie_list[0]["modifier"]}', inline=False)
        embed.add_field(name=sortie_list[1]['node'],
                        value=f'Mission: {sortie_list[1]["missionType"]} \n Conditions: {sortie_list[1]["modifier"]}', inline=False)
        embed.add_field(name=sortie_list[2]['node'],
                        value=f'Mission: {sortie_list[2]["missionType"]} \n Conditions: {sortie_list[2]["modifier"]}', inline=False)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Sorties(bot))
