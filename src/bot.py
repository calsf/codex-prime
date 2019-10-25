# https://github.com/WFCD/warframe-status
# https://docs.warframestat.us

from src import config
from src.cogs import (cetus, fissure, invasion, rivens, sortie)
import discord
from discord.ext import commands

# Bot setup
bot = commands.Bot(command_prefix='!')
bot.remove_command('help')
token = config.DISCORD_TOKEN
cetus.setup(bot)
fissure.setup(bot)
invasion.setup(bot)
rivens.setup(bot)
sortie.setup(bot)


@bot.event
async def on_ready():
    print('Bot Online!')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Invalid command. Enter !help for commands.")


@bot.command()
async def help(ctx):
    embed = discord.Embed(title='Command List:')
    embed.add_field(name='!cycle', value='Show status of current Cetus day/night cycle.', inline=False)
    embed.add_field(name='!atcycle <minutes>',
                    value='Activate alert notification for the next Cetus day/night cycle.\n'
                          '<minutes> 1-30 minutes before the next cycle || 5 minute default.',
                    inline=False)
    embed.add_field(name='!rmcycle', value='Stop being alerted for the next Cetus day/night cycle.', inline=False)
    embed.add_field(name='!fissures <relic or missiontype>', value='Show current void fissure missions based on'
                                                                   ' <relic or missiontype>.\n'
                                                                   '<relic> Lith, Meso, Neo, or Axi\n'
                                                                   '<missiontype> Capture, Survival, Extermination,'
                                                                   ' Excavation, Defense, Mobile Defense,'
                                                                   ' Rescue, Interception, Sabotage, Spy',
                    inline=False)
    embed.add_field(name='!atfissures <missiontype>', value='Activate alert notification for specific <missiontype> '
                                                            'Void Fissures. \n <missiontype>'
                                                            , inline=False)
    embed.add_field(name='!rmfissures', value='Stop being alerted for Void Fissures.', inline=False)
    embed.add_field(name='!invasions', value='Show all current Invasions.', inline=False)
    embed.add_field(name='!atinvasions <reward>', value='Activate alert notification for Invasions'
                                                        ' containing <reward>\n<reward> to alert for '
                                                        '(ex: "Strun" will look for any Strun pieces)', inline=False)
    embed.add_field(name='!rminvasions', value='Stop being alerted for Invasion rewards.', inline=False)
    embed.add_field(name='!sorties', value='Show current sortie missions.', inline=False)
    embed.add_field(name='!riven <weapon>', value='Show average prices for a <weapon> riven. '
                                                  '<weapon> riven', inline=False)
    await ctx.send(embed=embed)


bot.run(token)
