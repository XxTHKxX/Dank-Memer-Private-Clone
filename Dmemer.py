import discord
import psycopg2
import os
import time
import random
from itertools import cycle
from discord.ext import commands, tasks
# Importing libraries
 
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
# When bot is ready it'll start the status change routine and print the Ready message in the log

@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)} ms")
#No need to explain this one -.-

def connectsql():	
  DATABASE_URL = os.environ['DATABASE_URL']
  global conn
  conn = psycopg2.connect(DATABASE_URL, sslmode='require')
  global cur
  cur = conn.cursor()
# Acquiring database's URL, connecting and making a cursor to access the database

@bot.command()
async def init(ctx):
    connectsql() #Connect to the database
    cur.execute("CREATE TABLE data (id BIGINT, username TEXT, amount INTEGER)") #Start the database creation process
    for guild in bot.guilds: #Looping though all servers
	      for member in guild.members: #Looping though all members
	      	if member.bot == True:
	      		pass #Checking if a user is a bot, if True, skip this user
	      	else:
	          targetname = repr(member.name + "#" + member.discriminator)
	          cur.execute(f"INSERT INTO data (id, username, amount) VALUES ({member.id}, {targetname}, 5000)") #Adding member to database
	          await ctx.send(f"Member {targetname} has been added to the database") #Reporting to the user on who get added
	          time.sleep(0.75) #Waiting 0.75 seconds to bypass discord rate limit
	      	
    conn.commit() #Commiting the changes to the database
    conn.close() #Closing the database connection

@bot.command()
async def wipe(ctx):
	connectsql() # Connect to database
	cur.execute("DELETE FROM data") # Wipe all data from the table
	cur.execute("DROP TABLE IF EXISTS data") #Delete the table itself
	conn.commit() #Commit the change
	conn.close() #Close the connection
	await ctx.send("Table Wiped") #Report to user
	
@bot.command()
async def rich(ctx):
	connectsql() #Connect to database
	for guild in bot.guilds: #looping though all servers
		for member in guild.members: #looping though all members	
			cur.execute(f"SELECT * FROM data ORDER BY amount") #Search in the database about the user with that ID
			row = cur.fetchone() #Get the data on that user
			if row == None:
				break #If the data is not found, skip
			await ctx.send(f"ID: {row[0]}\nName: {row[1]}\nBalance: {row[2]}") #Reporting data
			time.sleep(0.75) #Wait 0.75 seconds
	conn.close() #Close connection
								
@bot.command()
async def rob(ctx, target : discord.Member):
	connectsql() #Connect to database
	attackerid = ctx.author.id #Get the ID of the attacker
	user = target #Get ID of the victim
	cur.execute(f"SELECT * FROM data WHERE id = {user.id}")
	row = cur.fetchone() #Get data of the victim
	if row == None:
		await ctx.send("Unable to find target") #Report if the user is not found
	targetbal = row[2] #Saving the balance data of the victim
	cur.execute(f"SELECT * FROM data WHERE id = {attackerid}") #Getting the data of the attacker
	row = cur.fetchone() #Get data of attacker
	if row == None:
		await ctx.send("Unable to find your profile, are you sure you're enrolled?") #Report if user not found
	attackerbal = row[2]	#Saving data of attacker
	successmin = 40 #Minimum success number
	roll1 = random.randint(1,100) # Generate first number
	if roll1 >= successmin: #Check if the attacker succeed
		stolenpercent = random.randint(3, 35) #Randomizing the percentage stolen
		stolen = round(targetbal * (stolenpercent / 100)) #Calculating the amount stolen and rounding it
		remain = targetbal - stolen
		attackernewbal = attackerbal + stolen
		# Math Time
		cur.execute(f"UPDATE data SET amount = {remain} WHERE id = {user.id}")
		cur.execute(f"UPDATE data SET amount = {attackernewbal} WHERE id = {attackerid}")
		#Updating the datas in the database
		await ctx.send(f"Successful Steal! You've swooped {stolen}, or {stolenpercent}% from {user}")
		#report to user
	else:
		roll2 = random.randint(1,100) #Randomizing number 2
		death = 10
		if roll2 <= death: #Check if that user is really gonna die
			cur.execute(f"UPDATE data SET amount = 0 WHERE id = {attackerid}") #Delete their money
			await ctx.send("Oh fuck, you tripped over a banana and hit your head in a pile of shit, and now you're dead")	#INSULT
		else:
			await ctx.send("You Failed the rob, noooob")	 #Report if they failed
	conn.commit() #Commit data to database
	conn.close() #Close connection
	

token = os.environ.get('BOT_TOKEN')
bot.run(token) #Getting the bot token and logging in with it
