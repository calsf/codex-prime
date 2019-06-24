# FISSURE COMMANDS:
# !fissures <relic> // !atfissures <"mission type"> // !rmfissures

import discord
from discord.ext import commands
import asyncio
from operator import itemgetter
from src import sess


class Fissures(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alert_dict = {}  # user: mission type, list of last checked missions of mission type

    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            await asyncio.gather(self.check_fissures(5))

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
                    embed.add_field(name=f'{mission["node"]}',
                                    value=f'{mission["missionType"]} - {mission["enemy"]}\n'
                                    f'{mission["tier"]} Fissure\n'
                                    f'{mission["eta"]}', inline=True)
                await ctx.send(embed=embed)
                return
            # Else show all void fissure missions
            else:
                for mission in relic_tiers[tier]:
                    embed.add_field(name=f'{mission["node"]}',
                                    value=f'{mission["missionType"]} - {mission["enemy"]}\n'
                                    f'{mission["tier"]} Fissure\n'
                                    f'{mission["eta"]}', inline=True)
        await ctx.send(embed=embed)

    # Add user of command to alert_dict to be notified of new <mission> void fissures
    @commands.command()
    async def atfissures(self, ctx, mission=''):
        valid = {'capture', 'survival', 'extermination', 'excavation', 'mobile defense', 'defense',
                 'rescue', 'interception', 'sabotage', 'spy'}
        try:
            if mission.lower() not in valid:
                await ctx.send(ctx.message.author.mention + ' Enter a valid mission type.\n'
                                                            'Capture, Survival, Extermination, Excavation, Defense, '
                                                            'Mobile Defense, Rescue, Interception, Sabotage, Spy')
            else:
                self.alert_dict[ctx.message.author] = [mission.title(), []]
                await ctx.send(
                    ctx.message.author.mention +
                    f' You will now be alerted for new {mission.title()} Void Fissures.')
        except ValueError:
            await ctx.send(ctx.message.author.mention + ' Enter a valid mission type.\n'
                                                        'Capture, Survival, Extermination, Excavation, Defense, '
                                                        'Mobile Defense, Rescue, Interception, Sabotage, Spy')

    # Remove user of command from the cetus_dict to no longer be notified of next day/night cycle
    @commands.command()
    async def rmfissures(self, ctx):
        try:
            self.alert_dict.pop(ctx.message.author)
            await ctx.send(ctx.message.author.mention + ' You are no longer being alerted'
                                                        ' for any Void Fissures.')
        except KeyError:
            await ctx.send(ctx.message.author.mention + ' You are currently not being alerted.')

    # THIS WILL BE PERIODICALLY CALLED on_ready
    # Check for new void fissure missions
    async def check_fissures(self, delay):
        # Wait before making request
        await asyncio.sleep(delay)
        fissures = await sess.request('fissures')

        fissures = sorted(fissures, key=itemgetter('tierNum'))
        embed = discord.Embed(title='Void Fissures')

        # Check each user's tracked mission type
        for user in self.alert_dict.keys():
            user_fissures = []
            for mission in fissures:
                if mission['missionType'].lower() == self.alert_dict[user][0].lower():
                    embed.add_field(name=f'{mission["node"]}',
                                    value=f'{mission["missionType"]} - {mission["enemy"]}\n'
                                    f'{mission["tier"]} Fissure\n'
                                    f'{mission["eta"]}', inline=True)
                    user_fissures.append(mission)

            # If fissure missions based on 'node' have been updated from last check, notify user
            if len(self.alert_dict[user][1]) != len(user_fissures):  # If lengths do not match, alert of update
                self.alert_dict[user][1] = user_fissures.copy()
                await user.send(f'{self.alert_dict[user][0]} missions have been updated!', embed=embed)
            else:
                for i in range(len(self.alert_dict[user][1])):  # Else check each mission node
                    if self.alert_dict[user][1][i]['node'] != user_fissures[i]['node']:
                        self.alert_dict[user][1] = fissures.copy()
                        await user.send(f'{self.alert_dict[user][0]} missions have been updated!', embed=embed)
                        return


def setup(bot):
    bot.add_cog(Fissures(bot))
