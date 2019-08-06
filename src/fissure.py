# FISSURE COMMANDS:
# !fissures <relic or missiontype> // !atfissures <relic or mission type> // !rmfissures

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
        print('Fissures Ready')

        while True:
            await asyncio.gather(self.check_fissures(5))

    @commands.command()
    async def fissures(self, ctx, *, filter_by=''):
        valid_type = ['capture', 'survival', 'extermination', 'excavation', 'mobile defense', 'defense',
                      'rescue', 'interception', 'sabotage', 'spy', 'hive']

        fissures = await sess.request('fissures')

        # Organize void fissure missions into mission type, default sort by relic type
        fissures = sorted(fissures, key=itemgetter('tierNum'))
        if filter_by.lower() in valid_type:
            filtered = {'capture': [], 'survival': [], 'extermination': [], 'excavation': [], 'mobile defense': [],
                        'defense': [], 'rescue': [], 'interception': [], 'sabotage': [], 'spy': [], 'hive': []}
            for mission in fissures:
                # Ignore any invalid mission types that are found
                try:
                    mission_type = mission['missionType'].lower()
                    filtered[mission_type].append(mission)
                except Exception as e:
                    print('Unknown mission type: ' + str(e))
        else:
            filtered = {'Lith': [], 'Meso': [], 'Neo': [], 'Axi': []}
            for mission in fissures:
                tier = mission['tierNum']
                if tier == 1:
                    filtered['Lith'].append(mission)
                elif tier == 2:
                    filtered['Meso'].append(mission)
                elif tier == 3:
                    filtered['Neo'].append(mission)
                elif tier == 4:
                    filtered['Axi'].append(mission)

        embed = discord.Embed(title=f'Void Fissures')
        for k in filtered.keys():
            # Show specific missions based on filtered_by
            if k.lower() == filter_by.lower():
                embed = discord.Embed(title=f'{k.title()} Void Fissures')  # Change title to filtered by Void Fissures
                embed.clear_fields()
                for mission in filtered[k]:
                    embed.add_field(name=f'{mission["node"]}',
                                    value=f'{mission["missionType"]} - {mission["enemy"]}\n'
                                    f'{mission["tier"]} Fissure\n'
                                    f'{mission["eta"]}', inline=True)
                await ctx.send(embed=embed)
                return
            # Else show all void fissure missions
            else:
                for mission in filtered[k]:
                    embed.add_field(name=f'{mission["node"]}',
                                    value=f'{mission["missionType"]} - {mission["enemy"]}\n'
                                    f'{mission["tier"]} Fissure\n'
                                    f'{mission["eta"]}', inline=True)
        await ctx.send(embed=embed)

    # Add user of command to alert_dict to be notified of new <filtered_by> void fissures
    @commands.command()
    async def atfissures(self, ctx, *, filtered_by=''):
        # Valid filters include mission types or relics
        valid = ['capture', 'survival', 'extermination', 'excavation', 'mobile defense', 'defense',
                 'rescue', 'interception', 'sabotage', 'spy', 'hive', 'lith', 'meso', 'neo', 'axi']
        try:
            if filtered_by.lower() not in valid:
                await ctx.send(ctx.message.author.mention + ' Enter a valid mission type or relic.\n'
                                                            'Mission Types: Capture, Survival, '
                                                            'Extermination, Excavation, Defense, '
                                                            'Mobile Defense, Rescue, Interception,'
                                                            ' Sabotage, Spy, Hive\n'
                                                            'Relics: Lith, Meso, Neo, Axi')
            else:
                self.alert_dict[ctx.message.author] = [filtered_by.title(), []]
                await ctx.send(
                    ctx.message.author.mention +
                    f' You will now be alerted for new {filtered_by.title()} Void Fissures.')
        except ValueError:
            await ctx.send(ctx.message.author.mention + ' Enter a valid mission type or relic.\n'
                                                        'Mission Types: Capture, Survival, '
                                                        'Extermination, Excavation, Defense, '
                                                        'Mobile Defense, Rescue, Interception, Sabotage, Spy, Hive\n'
                                                        'Relics: Lith, Meso, Neo, Axi')

    # Remove user of command from the alert_dict to no longer be notified of void fissures
    @commands.command()
    async def rmfissures(self, ctx):
        try:
            self.alert_dict.pop(ctx.message.author)
            await ctx.send(ctx.message.author.mention + ' You are no longer being alerted'
                                                        ' for any Void Fissures.')
        except KeyError:
            await ctx.send(ctx.message.author.mention + ' You are currently not being alerted.')

    # THIS WILL BE PERIODICALLY CALLED on_ready
    # Check for new/specific void fissure missions for each user
    async def check_fissures(self, delay):
        # Wait before making request
        await asyncio.sleep(delay)
        fissures = await sess.request('fissures')

        fissures = sorted(fissures, key=itemgetter('tierNum'))
        embed = discord.Embed(title='Void Fissures')

        relics = ['lith', 'meso', 'neo', 'axi']  # Valid relics

        # Check each user's tracked mission type
        for user in self.alert_dict.keys():
            embed.clear_fields()
            user_fissures = []

            # Check if user's filter is for relics/tier or mission type
            if self.alert_dict[user][0].lower() in relics:
                filter_val = 'tier'
            else:
                filter_val = 'missionType'

            # Iterate through all fissure missions and filter based on tier or mission type
            for mission in fissures:
                if mission[filter_val].lower() == self.alert_dict[user][0].lower():
                    embed.add_field(name=f'{mission["node"]}',
                                    value=f'{mission["missionType"]} - {mission["enemy"]}\n'
                                    f'{mission["tier"]} Fissure\n'
                                    f'{mission["eta"]}', inline=True)
                    user_fissures.append(mission)

            # If fissure missions based on 'node' have been updated from last check, notify user
            if len(self.alert_dict[user][1]) != len(user_fissures):  # If lengths do not match, alert of update
                self.alert_dict[user][1] = user_fissures.copy()
                await user.send(f'{self.alert_dict[user][0]} Void Fissures have been updated!', embed=embed)
            else:
                for i in range(len(self.alert_dict[user][1])):  # Else check each mission node
                    if self.alert_dict[user][1][i]['node'] != user_fissures[i]['node']:
                        self.alert_dict[user][1] = fissures.copy()
                        await user.send(f'{self.alert_dict[user][0]} Void Fissures have been updated!', embed=embed)
                        return


def setup(bot):
    bot.add_cog(Fissures(bot))
