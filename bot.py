# https://github.com/WFCD/warframe-status
# https://docs.warframestat.us

import config
import discord
from discord.ext import commands
import aiohttp
import asyncio

# Bot setup
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
token = config.DISCORD_TOKEN


# Create single session
async def create_session():
    return aiohttp.ClientSession()
loop = asyncio.get_event_loop()
session = loop.run_until_complete(create_session())

# Users to notify for next day/night cycle // user: [time before to notify, has been notified]
cetus_dict = {}
is_day = True


# Make request and convert json data
async def endpoint(data):
    async with session.get(f'https://api.warframestat.us/pc/{data}') as res:
        return await res.json()


@bot.event
async def on_ready():
    print('Bot Online!')

    # Periodically check
    while True:
        await asyncio.gather(check_cycle(20))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command.")


# Check the status of the current cycle and remaining time left
@bot.command()
async def cycle(ctx):
    cetus_cycle = await endpoint('cetusCycle')
    time_left = cetus_cycle.get('timeLeft')
    if cetus_cycle.get('isDay'):
        current_cycle = 'Day'
    else:
        current_cycle = 'Night'

    embed = discord.Embed()
    embed.add_field(name='Current Cycle', value=current_cycle, inline=False)
    embed.add_field(name='Time Left', value=time_left, inline=False)
    await ctx.send(embed=embed)


# Add user of command to the cetus_dict to be notified of next day/night cycle, default time to notify will be 5 minutes
@bot.command()
async def atcycle(ctx, time='5'):
    try:
        if int(time) > 30 or int(time) < 1:
            await ctx.send(ctx.message.author.mention + ' Enter a time between 1-30')
        else:
            cetus_dict[ctx.message.author] = [time, False]
            await ctx.send(
                ctx.message.author.mention +
                f' You will now be alerted {time} minutes before the next Cetus day/night cycle.')
    except ValueError:
        await ctx.send(ctx.message.author.mention + ' Enter a time between 1-30.')


# Remove user of command from the cetus_dict to no longer be notified of next day/night cycle
@bot.command()
async def rmcycle(ctx):
    try:
        cetus_dict.pop(ctx.message.author)
        await ctx.send(ctx.message.author.mention + ' You are no longer being alerted'
                                                    ' for the next Cetus day/night cycle.')
    except KeyError:
        await ctx.send(ctx.message.author.mention + ' You are currently not being alerted.')


@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Command List:')
    embed.add_field(name='!cycle', value='Show status of current Cetus day/night cycle.', inline=False)
    embed.add_field(name='!acycle <minutes>', value='Activate alert notification for the next Cetus day/night cycle, '
                                                    '<minutes> before the next cycle.\n'
                                                    'Will only notify within 1-30 minutes before (5 minute default).',
                    inline=False)
    embed.add_field(name='!rmcycle', value='Stop being alerted for the next Cetus day/night cycle.', inline=False)
    await ctx.send(embed=embed)


# THIS WILL BE PERIODICALLY CALLED on_ready
# Check time until next cycle, notify if needed
async def check_cycle(delay):
    await asyncio.sleep(delay)
    # message/ping user below
    cetus_cycle = await endpoint('cetusCycle')

    # Check for time left (if has an hour or no minutes, default to 100 time_check
    time_left = cetus_cycle.get('timeLeft')
    if time_left.__contains__('h') or not time_left.__contains__('m'):
        time_check = 100  # Will never notify for 100 as notify range is 1-59
    else:
        time_check = time_left.split('m')[0]  # Only check for minutes

    # Check for next cycle
    if cetus_cycle.get('isDay'):
        next_cycle = 'Night'
    else:
        next_cycle = 'Day'

    # Notify each user if time left matches their time to notify
    # Do not notify user if they have already been notified in this night/day cycle
    for user in cetus_dict.keys():
        user_list = cetus_dict.get(user)
        if user_list[0] == time_check and not user_list[1]:
            cetus_dict[user][1] = True
            await user.send(f'{time_left} until {next_cycle}.')

    # Check if current cycle matches last cycle check
    # If not, update cycle and reset has notified for all users to False
    global is_day
    if cetus_cycle.get('isDay') != is_day:
        is_day = cetus_cycle.get('isDay')
        for user in cetus_dict:
            cetus_dict[user][1] = False


bot.run(token)
