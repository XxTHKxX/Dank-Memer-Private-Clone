import discord
import pg8000
import os
from itertools import cycle
from discord.ext import commands, tasks
 
bot = commands.Bot(command_prefix='n! ')
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
"""
URL IS postgres://vhmsoqilfojjga:3c8050ea8af0ab15e5fff18a9a18fce9e120b8db63a994a07f7dbe4d3a3f4804@ec2-52-202-146-43.compute-1.amazonaws.com:5432/demml3ogknu62f
"""
con = pg8000.connect(user='vhmsoqilfojjga', host='ec2-52-202-146-43.compute-1.amazonaws.com', database = 'demml3ogknu62f', ssl_context=True)

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
