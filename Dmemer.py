import discord
import psycopg2
import os
import random
import asyncio
import requests
from urllib.parse import unquote
from itertools import cycle
from discord.ext import commands, tasks
# Importing libraries


bot = commands.Bot(command_prefix=['n!', 'N!'], case_insensitive = True)
#Status Change
status = cycle(['Looking at the records', 'transferring money', 'Waiting for drama'])
@tasks.loop(seconds=2)
async def change_status():
	await bot.change_presence(activity=discord.Game(next(status)))
	
def connectsql():
	DATABASE_URL = os.environ['DATABASE_URL']
	global conn
	conn = psycopg2.connect(DATABASE_URL, sslmode='require')
	global cur
	cur = conn.cursor()
# Acquiring database's URL, connecting and making a cursor to access the database

@tasks.loop(seconds=60)
async def drop():
	gamechannel = bot.get_channel(724274805381267498)
	chance = random.randint(1,200)
	number = random.randint(1000,9999)
	amount = random.randint(0,10000)
	def check(m):
		if m.content.isnumeric() == True:
			return int(m.content) == number and m.channel == gamechannel
		else:
			pass
	if chance >=199:
		bomb = random.randint(0,100)
		if bomb != 1:
			connectsql()
			await gamechannel.send(f"Quick! A lootbox has been dropped! Type '{number}' to get it!")
			try:
				answer = await bot.wait_for('message', check=check, timeout = 8.0)
			except asyncio.TimeoutError:
				await gamechannel.send("Oh well, look like no one's gonna loot it, Imma donate it to charity")
			else:
				if int(answer.content) == number:
					cur.execute(f"SELECT * FROM data WHERE id = {answer.author.id}")
					data = cur.fetchone()
					currentbal = data[2]
					newbal = currentbal + amount
					cur.execute(f"UPDATE data SET amount = {newbal} WHERE id = {answer.author.id}")
					await gamechannel.send(f"Drop looted by {answer.author}! You got {amount}")
			conn.commit()
			conn.close()
		else:
			connectsql()
			await gamechannel.send(f"Quick! A lootbox has been dropped! Type '{number}' to get it!")
			try:
				answer = await bot.wait_for('message', check=check, timeout = 8.0)
			except asyncio.TimeoutError:
				await gamechannel.send("Oh well, look like no one's gonna loot it, Imma donate it to charity")
			else:
				if int(answer.content) == number:
					cur.execute(f"SELECT * FROM data WHERE id = {answer.author.id}")
					data = cur.fetchone()
					newbal = 0
					cur.execute(f"UPDATE data SET amount = {newbal} WHERE id = {answer.author.id}")
					await gamechannel.send(f"Lootbox looted by {answer.author}! Unfortunately, there was an activated bomb inside the lootbox. You explode in a spectacular show of flesh and blood. You also lost all your money.")
			conn.commit()
			conn.close()
			
			
			
ownerid = [708645600165625872, 419742289188093952]

@bot.event
async def on_ready():
	download_questions()
	change_status.start()
	drop.start()
	global antinsfw
	antinsfw = False
	print('Ready.')
# When bot is ready it'll start the status change routine and print the Ready message in the log


@bot.command()
async def ping(ctx):
	await ctx.send(f"Pong! {round(bot.latency * 1000)} ms")
#No need to explain this one -.-


@commands.has_permissions(administrator=True)
@bot.command()
async def nonsfw(ctx, option):
	global antinsfw
	if option == 'yes':
		antinsfw = True
		await ctx.send('Beginning to cleanise this chat')
	elif option == 'no':
		antinsfw = False
		await ctx.send('Okay, entering the dark side')
		
						
@commands.has_permissions(administrator=True)
@bot.command()
async def init(ctx):
	connectsql() #Connect to the database
	cur.execute("CREATE TABLE data (id BIGINT, username TEXT, amount INTEGER)") #Start the database creation process
	conn.commit()
	conn.close()
	connectsql()
	cur.execute("CREATE TABLE trivia (id BIGINT, category TEXT, difficulty TEXT, question TEXT, correct TEXT, wrong1 TEXT, wrong2 TEXT, wrong3 TEXT)")
	conn.commit()
	conn.close()
	connectsql()
	message = ''
	for guild in bot.guilds: #Looping though all servers
		for member in guild.members: #Looping though all members
			if member.bot == True:
				pass #Checking if a user is a bot, if True, skip this user
			else:
				targetname = repr(member.name + "#" + member.discriminator)
				cur.execute(f"INSERT INTO data (id, username, amount) VALUES  ({member.id}, {targetname}, 5000)") #Adding member to database
				message = message + '\n' + (f"Member {targetname} has been added to the database")
	await ctx.send(message)	
	conn.commit() #Commiting the changes to the database
	conn.close() #Closing the database connection
	download_questions()
	await ctx.send('Questions added to database')
	
@commands.has_permissions(administrator=True)
@bot.command()
async def wipe(ctx):
	connectsql() # Connect to database
	cur.execute("DELETE FROM data") # Wipe all data from the table
	cur.execute("DELETE FROM trivia")
	cur.execute("DROP TABLE IF EXISTS data") #Delete the table itself
	cur.execute("DROP TABLE IF EXISTS trivia")
	conn.commit() #Commit the change
	conn.close() #Close the connection
	await ctx.send("Table Wiped") #Report to user
	
@bot.command()
async def rich(ctx):
	connectsql() #Connect to database
	currentdata = ''
	for guild in bot.guilds: #looping though all servers
		cur.execute(f"SELECT * FROM data ORDER BY amount DESC") #Search in the database about the user with that ID
		rows = cur.fetchall() #Get the data
		for row in rows:
			if row == None:
				break #If the data is not found, skip
			currentdata = currentdata + "\n" + (f"Name: {row[1]}\nBalance: {row[2]}") #Reporting data
			
	await ctx.send(currentdata)
	conn.close() #Close connection
	
	
@bot.command()
async def bal(ctx, target : discord.Member = None):
	if target == None:
		target = ctx.author
	connectsql()
	embed=discord.Embed(color=0xffff00)
	message = f"Balance of {target}"
	cur.execute(f"SELECT * FROM data WHERE id = {target.id}")
	data = cur.fetchone()
	amount = data[2]
	embed.add_field(name=message, value=amount, inline=True)
	embed.set_footer(text="Bot made by Xx_THK_xX")
	await ctx.send(embed=embed)
	conn.close()
	
	
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
	attackerbal = row[2]    #Saving data of attacker
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
			await ctx.send("Oh fuck, you tripped over a banana and hit your head in a pile of shit, and now you're dead")   #INSULT
		else:
			await ctx.send("You Failed the rob, noooob")     #Report if they failed
	conn.commit() #Commit data to database
	conn.close() #Close connection
	
@commands.has_permissions(administrator=True)
@bot.command()
async def forcedrop(ctx):
	gamechannel = bot.get_channel(724274805381267498)
	number = random.randint(1000,9999)
	amount = random.randint(0,10000)
	def check(m):
		if m.content.isnumeric() == True:
			return int(m.content) == number and m.channel == gamechannel
		else:
			pass
	if True:
		bomb = random.randint(1,99)
		if bomb != 1:
			connectsql()
			await gamechannel.send(f"Quick! A lootbox has been dropped! Type '{number}' to get it!")
			try:
				answer = await bot.wait_for('message', check=check, timeout = 8.0)
			except asyncio.TimeoutError:
				await gamechannel.send("Oh well, look like no one's gonna loot it, Imma donate it to charity")
			else:
				if int(answer.content) == number:
					cur.execute(f"SELECT * FROM data WHERE id = {answer.author.id}")
					data = cur.fetchone()
					currentbal = data[2]
					newbal = currentbal + amount
					cur.execute(f"UPDATE data SET amount = {newbal} WHERE id = {answer.author.id}")
					await gamechannel.send(f"Drop looted by {answer.author}! You got {amount}")
			conn.commit()
			conn.close()
		else:
			connectsql()
			await gamechannel.send(f"Quick! A lootbox has been dropped! Type '{number}' to get it!")
			try:
				answer = await bot.wait_for('message', check=check, timeout = 8.0)
			except asyncio.TimeoutError:
				await gamechannel.send("Oh well, look like no one's gonna loot it, Imma donate it to charity")
			else:
				if int(answer.content) == number:
					cur.execute(f"SELECT * FROM data WHERE id = {answer.author.id}")
					data = cur.fetchone()
					newbal = 0
					cur.execute(f"UPDATE data SET amount = {newbal} WHERE id = {answer.author.id}")
					await gamechannel.send(f"Lootbox looted by {answer.author}!, unfortunately, there's a bomb inside and you died")
			conn.commit()
			conn.close()
			
					
def download_questions():
	print('Downloading questions from Open Trivia DB...')
	api_url = 'https://opentdb.com/api.php?amount=50&type=multiple&encode=url3986'
	r = requests.get(api_url)
	
	connectsql()
	cur.execute("DELETE FROM trivia")
	conn.commit()
	conn.close()
	
	connectsql()
	api_result = r.json()
	questions = api_result['results']
	id = 0
	for q in questions:
		id = id + 1
		category = repr(unquote(q['category']))
		difficulty = repr(unquote(q['difficulty']))
		question = repr(unquote(q['question']))
		correctans = repr(unquote(q['correct_answer']))
		badans1 = repr(unquote(q['incorrect_answers'][0]))
		badans2 = repr(unquote(q['incorrect_answers'][1]))
		badans3 = repr(unquote(q['incorrect_answers'][2]))
		cur.execute(f"INSERT INTO trivia (id, category, difficulty, question, correct, wrong1, wrong2, wrong3) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (id, category, difficulty, question, correctans, badans1, badans2, badans3))
		conn.commit()
		conn.close()
		
def getquestion():
	connectsql()
	questionid = random.randint(1,50)
	cur.execute(f"SELECT * FROM trivia WHERE id = {questionid}")
	data = cur.fetchone()
	cat = data[1]
	diff = data[2]
	question = data[3]
	correctans = data[4]
	wrongans = data[5]
	allans = correctans + wrongans
	random.shuffle(allans)
	response = "category:" + cat + "\n" + "Difficulty:" + diff + "\n" + "Question:" + question + "\n" + allans
	return response
	
		
@bot.command()
async def triviatest(ctx):
	await ctx.send('Getting Question...')
	answer = getquestion()
	await ctx.send(answer)
	
@bot.event
async def on_message(message):
	global antinsfw
	if message.author.id == 285480424904327179 and antinsfw == True:
		await message.delete()
	else:
		await bot.process_commands(message)
		
		
		
		
		
token = os.environ.get('BOT_TOKEN')
bot.run(token) #Getting the bot token and logging in with it

