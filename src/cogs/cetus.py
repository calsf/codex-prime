#CETUS COMMANDS:
# !cycle // !atcycle <minutes> // !rmcycle

import discord
from discord.ext import commands
import asyncio
from src import sess


class Cetus(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.cetus_dict = {}  # user : time before cycle, has been notified
        self.is_day = True  # To check if the cycle has changed since last check_cycle/reset user notify

    @commands.Cog.listener()
    async def on_ready(self):
        # Set initial cycle
        cycle = await sess.request('cetusCycle')
        while cycle is 0:
            print("Could not retrieve data. Trying again.")
            cycle = await sess.request('cetusCycle')

        self.is_day = cycle.get('isDay')

        print('Cetus Cycle Online')

        # Periodically check
        while True:
            await asyncio.gather(self.check_cycle(30))

    # Check the status of the current cycle and remaining time left
    @commands.command()
    async def cycle(self, ctx):
        cetus_cycle = await sess.request('cetusCycle')
        if cetus_cycle is 0:
            print("Could not retrieve data.")
            return

        time_left = cetus_cycle.get('timeLeft')
        if cetus_cycle.get('isDay'):
            current_cycle = 'Day'
            next_cycle = 'Night'
        else:
            current_cycle = 'Night'
            next_cycle = 'Day'

        embed = discord.Embed()
        embed.add_field(name='Current Cycle', value=current_cycle, inline=False)
        embed.add_field(name=f'Time Left Until {next_cycle}', value=time_left, inline=False)
        await ctx.send(embed=embed)

    # Add user of command to the cetus_dict to be notified of next day/night cycle
    # Default time to notify will be 5 minutes
    @commands.command()
    async def atcycle(self, ctx, time='5'):
        try:
            if int(time) > 30 or int(time) < 1:
                await ctx.send(ctx.message.author.mention + ' Enter a time between 1-30')
            else:
                self.cetus_dict[ctx.message.author] = [time, False]

                await ctx.send(
                    ctx.message.author.mention +
                    f' You will now be alerted {time} minutes before the next Cetus day/night cycle.')
        except ValueError:
            await ctx.send(ctx.message.author.mention + ' Enter a time between 1-30.')

    # Remove user of command from the cetus_dict to no longer be notified of next day/night cycle
    @commands.command()
    async def rmcycle(self, ctx):
        try:
            self.cetus_dict.pop(ctx.message.author)
            await ctx.send(ctx.message.author.mention + ' You are no longer being alerted'
                                                        ' for the next Cetus day/night cycle.')
        except KeyError:
            await ctx.send(ctx.message.author.mention + ' You are currently not being alerted.')

    # THIS WILL BE PERIODICALLY CALLED on_ready
    # Check time until next cycle, notify if needed
    async def check_cycle(self, delay):
        # Wait before making request
        await asyncio.sleep(delay)
        cetus_cycle = await sess.request('cetusCycle')
        if cetus_cycle is 0:
            print("Could not retrieve data.")
            return

        # Check for time left (if has an hour or no minutes, default to 100 time_check
        time_left = cetus_cycle.get('timeLeft')
        if time_left.__contains__('h') or not time_left.__contains__('m'):
            time_check = 100  # Will never notify for 100 due to being outside notify range
        else:
            time_check = time_left.split('m')[0]  # Only check for minutes

        # Check for next cycle
        if cetus_cycle.get('isDay'):
            next_cycle = 'Night'
        else:
            next_cycle = 'Day'

        # Notify each user if time left is less than or equal to their time to notify
        # Do not notify user if they have already been notified in this night/day cycle
        for user in self.cetus_dict.keys():
            user_list = self.cetus_dict.get(user)
            if user_list[0] >= time_check and not user_list[1]:
                self.cetus_dict[user][1] = True
                await user.send(f'{time_left} until {next_cycle}.')

        # Check if current cycle matches last cycle check
        # If not, update cycle and reset has notified for all users to False
        if cetus_cycle.get('isDay') != self.is_day:
            self.is_day = cetus_cycle.get('isDay')
            for user in self.cetus_dict:
                self.cetus_dict[user][1] = False


def setup(bot):
    bot.add_cog(Cetus(bot))
