# https://github.com/WFCD/warframe-status
# https://docs.warframestat.us

import config
import discord
from discord.ext import commands
import aiohttp
import asyncio

bot = commands.Bot(command_prefix='!')
token = config.DISCORD_TOKEN
cetus_list = []


# Single session
async def create_session():
    return aiohttp.ClientSession()
loop = asyncio.get_event_loop()
session = loop.run_until_complete(create_session())


# Make request and convert json data
async def endpoint(data):
    async with session.get(f'https://api.warframestat.us/pc/{data}') as res:
        info = await res.json()
        return info


@bot.event
async def on_ready():
    print('Bot Online!')

    # Periodically check
    while True:
        await asyncio.gather(check_cycle(2))


# Check the status of the current cycle and remaining time left
@bot.command()
async def cycle(ctx):
    cetus_cycle = await endpoint('cetusCycle')
    time_left = cetus_cycle.get('timeLeft')
    if cetus_cycle.get('isDay'):
        current_cycle = 'Day'
    else:
        current_cycle = 'Night'
    await ctx.send(f'Currently: {current_cycle}\nTime Left: {time_left}')


# Add user of command to the cetus_list to be notified of next day/night cycle
@bot.command()
async def alert_cycle(ctx):
    if ctx.message.author not in cetus_list:
        cetus_list.append(ctx.message.author)
        await ctx.send(ctx.message.author.mention + ' You will now be alerted before the next Cetus day/night cycle.')
    else:
        await ctx.send(ctx.message.author.mention + ' You are already being alerted for the next Cetus day/night cycle.')


# Remove user of command from the cetus_list to no longer be notified of next day/night cycle
@bot.command()
async def remove_cycle(ctx):
    if ctx.message.author not in cetus_list:
        await ctx.send(ctx.message.author.mention + ' You aren\'t even being alerted!')
    else:
        cetus_list.remove(ctx.message.author)
        await ctx.send(ctx.message.author.mention + ' You are no longer being alerted'
                                                    ' for the next Cetus day/night cycle.')


# Check time until next cycle, notify if needed // This will be called periodically on_ready
async def check_cycle(delay):
    await asyncio.sleep(delay)
    # message/ping user below
    cetus_cycle = await endpoint('cetusCycle')
    time_left = cetus_cycle.get('timeLeft')
    if cetus_cycle.get('isDay'):
        next_cycle = 'Night'
    else:
        next_cycle = 'Day'
    for user in cetus_list:
        await user.send(f'{time_left} until {next_cycle}.')


bot.run(token)
