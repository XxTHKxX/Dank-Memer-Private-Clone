import discord
import pg8000
import os
from itertools import cycle
from discord.ext import commands, tasks
 
bot = commands.Bot(command_prefix=' ')
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
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)} ms")

DATABASE_URL = os.environ['DATABASE_URL']
con = pg8000.connect(DATABASE_URL, sslmode='require')

@bot.command()
async def initalize(ctx):
	  await con.run("DROP TABLE IF EXISTS data")
	  await con.run("CREATE TABLE data (id TEXT, amount INTEGER)")
	  for guild in bot.guilds:
	      for member in guild.members:
	      	con.run(f"INSERT INTO data VALUES ({member.id}), (15000) ")
	      	await ctx.send(f"Member {member.name}{member.discriminator} has been added to the database")

token = os.environ.get('BOT_TOKEN')
bot.run(token)
