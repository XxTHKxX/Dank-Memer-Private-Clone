import discord
import os
from itertools import cycle
from discord.ext import commands, tasks
 
bot = commands.Bot(command_prefix='TDM ')
#Status Change
status = cycle(['Looking at the records', 'transferring money', 'Waiting for drama'])
@tasks.loop(seconds=2)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status)))
@bot.event
async def on_ready():
    change_status.start()
    print('Ready.')
 

@bot.command()
async def pingx(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)} ms")
 

@bot.command()
@commands.has_permissions(manage_guild=True)
async def load(ctx, extension):
    bot.load_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} has been loaded')
    print(f'{extension} has been loaded')

@bot.command()
@commands.has_permissions(manage_guild=True)
async def unload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    await ctx.send(f'{extension} has been unloaded')
    print(f'{extension} has been unloaded')

@bot.command()
@commands.has_permissions(manage_guild=True)
async def reload(ctx, extension):
    bot.unload_extension(f'cogs.{extension}')
    bot.load_extension(f'cogs.{extension}')
    print(f'{extension} has been reloaded')
    await ctx.send(f'{extension} has been reloaded')


@load.error
async def load_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(">>> Error! Missing required argument! Please specify the module to load")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(">>> Error! Missing Permission! You don't have the **Manage Server** permission to run this command")

@unload.error
async def unload_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(">>> Error! Missing required argument! Please specify the module to unload")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(">>> Error! Missing Permission! You don't have the **Manage Server** permission to run this command")   

@reload.error
async def reload_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(">>> Error! Missing required argument! Please specify the module to reload")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send(">>> Error! Missing Permission! You don't have the **Manage Server** permission to run this command")

for filename in os.listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f'cogs.{filename[:-3]}')

token = ''
bot.run(token)
