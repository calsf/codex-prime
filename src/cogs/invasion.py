#INVASION COMMANDS:
# !invasions  // !atinvasions <reward>  // !rminvasions

import discord
from discord.ext import commands
import asyncio
from src import sess


class Invasions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.alert_dict = {}  # user: reward, list of prev invasions with reward

    @commands.Cog.listener()
    async def on_ready(self):
        print('Invasions Online')
        # Periodically check
        while True:
            await asyncio.gather(self.check_invasions(50))

    @commands.command()
    async def invasions(self, ctx):
        inv = await sess.request('invasions')
        if inv is 0:
            print("Could not retrieve data.")
            return

        embed = discord.Embed(title="Invasions")

        # Organize invasions into description/type
        inv_dict = {}  # example: {GrineerOffensive: [{mission}, {mission}], }
        for i in inv:
            if not i['completed']:  # Do not add invasions that have been completed
                if i['desc'] in inv_dict:
                    inv_dict[i['desc']].append(i)
                else:
                    inv_dict[i['desc']] = []
                    inv_dict[i['desc']].append(i)

        # Show invasion information grouped via description/type
        for key, li in inv_dict.items():
            info = ''
            for v in li:
                node = v['node']
                atk_reward = v['attackerReward']['asString'] or 'N/A'
                def_reward = v['defenderReward']['asString'] or 'N/A'
                attackers = v['attackingFaction']
                defenders = v['defendingFaction']
                info += node + ': \n' + attackers + f' [{atk_reward}]' + ' vs ' + defenders + f' [{def_reward}]\n'
            embed.add_field(name=f'{key}', value=f'{info}', inline=False)

        await ctx.send(embed=embed)

    # Add user of command to the alert_dict to be alerted of invasions with specific reward
    @commands.command()
    async def atinvasions(self, ctx, *, reward=''):
        try:
            if not reward:
                await ctx.send(ctx.message.author.mention + ' Enter an invasion reward to be alerted for.')
            else:
                self.alert_dict[ctx.message.author] = [reward, []]

                await ctx.send(
                    ctx.message.author.mention +
                    f' You will now be alerted for invasions with a {reward.title()} reward.')
        except ValueError:
            await ctx.send(ctx.message.author.mention + ' Enter an invasion reward to be alerted for.')

    # Remove user of command from the alert_dict to no longer be notified of invasion rewards
    @commands.command()
    async def rminvasions(self, ctx):
        try:
            self.alert_dict.pop(ctx.message.author)
            await ctx.send(ctx.message.author.mention + ' You are no longer being alerted'
                                                        ' for the next Cetus day/night cycle.')
        except KeyError:
            await ctx.send(ctx.message.author.mention + ' You are currently not being alerted.')

    # THIS WILL BE PERIODICALLY CALLED on_ready
    # Check for invasions with specific rewards for each user
    async def check_invasions(self, delay):
        # Wait before making request
        await asyncio.sleep(delay)
        inv = await sess.request('invasions')
        if inv is 0:
            print("Could not retrieve data.")
            return

        embed = discord.Embed(title="Invasions")

        # Organize invasions into description/type
        inv_dict = {}  # example: {GrineerOffensive: [{mission}, {mission}], }
        for i in inv:
            if not i['completed']:  # Do not add invasions that have been completed
                if i['desc'] in inv_dict:
                    inv_dict[i['desc']].append(i)
                else:
                    inv_dict[i['desc']] = []
                    inv_dict[i['desc']].append(i)

        # Check each user's tracked reward and notify of any missions with their specific reward
        for user in self.alert_dict.keys():
            embed.clear_fields()
            user_inv = []
            for key, li in inv_dict.items():
                info = ''
                for v in li:
                    if self.alert_dict[user][0].lower() in v['attackerReward']['asString'].lower() \
                            or self.alert_dict[user][0].lower() in v['defenderReward']['asString'].lower():
                        user_inv.append(v)
                        node = v['node']
                        atk_reward = v['attackerReward']['asString'] or 'N/A'
                        def_reward = v['defenderReward']['asString'] or 'N/A'
                        attackers = v['attackingFaction']
                        defenders = v['defendingFaction']
                        info += node + ': \n' + attackers + f' [{atk_reward}]' + ' vs ' + defenders + f' [{def_reward}]\n'
                if info != '':
                    embed.add_field(name=f'{key}', value=f'{info}', inline=False)

            # Check if need to notify user
            if len(self.alert_dict[user][1]) != len(user_inv):  # If lengths do not match, alert of update
                self.alert_dict[user][1] = user_inv.copy()
                await user.send(f'Invasions with {self.alert_dict[user][0].title()} reward has been updated!',
                                embed=embed)
            else:
                for i in range(len(self.alert_dict[user][1])):
                    if self.alert_dict[user][1][i]['node'] != user_inv[i]['node']:
                        self.alert_dict[user][1] = user_inv.copy()
                        await user.send(f'Invasions with {self.alert_dict[user][0].title()} reward has been updated!',
                                        embed=embed)


def setup(bot):
    bot.add_cog(Invasions(bot))
