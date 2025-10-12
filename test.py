import discord
from discord import app_commands
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# bot is ready and currently turned on
@bot.event
async def on_ready():
    print(f"hello time to work: {bot.user.name}")

# sends the user a welcome message when they join the server 
# (!!! currently in dms, could change later)
@bot.event
async def on_member_join(member):
    await member.send(f"welcome to {discord.guild.name}, {bot.user.name}")

#reads all messages
@bot.event
async def on_message(message):
    #if the user who sent the message is the bot itself, ignore
    if message.author == bot.user:
        return
    
    #the bot will delete the message if it has the word "shit" in it 
    if "shit" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} DONT SAY THAT WORD 3:<")

    # !!! DO NOT DELETE !!!
    await bot.process_commands(message)

# this is how you run a bot command
@bot.command()
async def hello(ctx):
    await ctx.send(f"hello! {ctx.author.mention}")

# we need a random role for this to work
test_role = "test role"

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=test_role)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"i have giveth '{test_role}' to {ctx.author.mention}.")
    else:
        await ctx.send(f"role DOESNT EXIST.")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=test_role)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"i have taketh '{test_role}' from {ctx.author.mention}.")
    else:
        await ctx.send(f"role DOESNT EXIST.")

@bot.command()
async def dm(ctx, *, message: str):
    await ctx.author.send(f"you said: {message}")

@bot.command()
async def reply(ctx):
    await ctx.reply(f"i reply :3")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)
