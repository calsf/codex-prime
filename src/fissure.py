# FISSURE COMMANDS:
# !fissures <relic>

import discord
from discord.ext import commands
from operator import itemgetter
from src import sess


class Fissures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def fissures(self, ctx, relic=''):
        fissures = await sess.request('fissures')

        # Organize void fissure missions into relic tiers
        fissures = sorted(fissures, key=itemgetter('tierNum'))
        relic_tiers = {'Lith': [], 'Meso': [], 'Neo': [], 'Axi': []}
        for mission in fissures:
            tier = mission['tierNum']
            if tier == 1:
                relic_tiers['Lith'].append(mission)
            elif tier == 2:
                relic_tiers['Meso'].append(mission)
            elif tier == 3:
                relic_tiers['Neo'].append(mission)
            elif tier == 4:
                relic_tiers['Axi'].append(mission)

        embed = discord.Embed(title='Void Fissures')
        for tier in relic_tiers.keys():
            # Show specific relic missions if specified
            if tier.lower() == relic.lower():
                embed = discord.Embed(title=f'{tier} Fissures')
                embed.clear_fields()
                for mission in relic_tiers[tier]:
                    embed.add_field(name=f'{mission["node"]} {mission["eta"]} Remaining',
                                    value=f'{mission["missionType"]} - {mission["enemy"]}\n'
                                    f'{mission["tier"]} Fissure\n')
                await ctx.send(embed=embed)
                return
            # Else show all void fissure missions
            else:
                for mission in relic_tiers[tier]:
                    embed.add_field(name=f'{mission["node"]} {mission["eta"]} Remaining',
                                    value=f'{mission["missionType"]} - {mission["enemy"]}\n'
                                    f'{mission["tier"]} Fissure\n')
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fissures(bot))
