# https://github.com/WFCD/warframe-status
# https://docs.warframestat.us

from src import config
import discord
from discord.ext import commands

# Bot setup
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
token = config.DISCORD_TOKEN

# Load extensions
bot.load_extension('cetus')
bot.load_extension('sortie')
bot.load_extension('fissure')


@bot.event
async def on_ready():
    print('Bot Online!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command.")


@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Command List:')
    embed.add_field(name='!cycle', value='Show status of current Cetus day/night cycle.', inline=False)
    embed.add_field(name='!acycle <minutes>',
                    value='Activate alert notification for the next Cetus day/night cycle.\n'
                          '1-30 <minutes> before the next cycle || 5 minute default.',
                    inline=False)
    embed.add_field(name='!rmcycle', value='Stop being alerted for the next Cetus day/night cycle.', inline=False)
    embed.add_field(name='!sorties', value='Show current sortie missions.', inline=False)
    embed.add_field(name='!fissures <relic>', value='Show current void fissure missions based on <relic>.\n'
                                                    'Lith, Meso, Neo, or Axi <relic> || All relics default',
                    inline=False)
    await ctx.send(embed=embed)


bot.run(token)
