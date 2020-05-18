import discord
import psycopg2
import os
import time
from itertools import cycle
from discord.ext import commands, tasks
 
bot = commands.Bot(command_prefix='n!')
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

conn = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = conn.cursor()
@bot.command()
async def init(ctx):
    cur.execute("CREATE TABLE data (id BIGINT, amount INTEGER)")
    for guild in bot.guilds:
	      for member in guild.members:
	      	cur.execute(f"INSERT INTO data (id, amount) VALUES ({member.id}, 5000) ")
	      	await ctx.send(f"Member {member.name}#{member.discriminator} has been added to the database")
	      	time.sleep(1)
    conn.commit()

@bot.command()
async def wipe(ctx):
	cur.execute("DELETE FROM data")
	cur.execute("DROP TABLE IF EXISTS data")
	conn.commit()
	await ctx.send("Table Wiped")
	
@bot.command()
async def list(ctx):
	for guild in bot.guilds:
		for member in guild.members:
			targetid = member.id
			cur.execute(f"SELECT * FROM data WHERE id = {targetid}")
			while True:
				row = cur.fetchone()
				if row == None:
					break
				await ctx.send(f"ID: {row[0]}\nName: {member.name}#{member.discriminator}\nBalance: {row[1]}")
			
	

token = os.environ.get('BOT_TOKEN')
bot.run(token)
