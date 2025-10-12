import discord
from discord import app_commands
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()


# -_-_-_-_-_-_-_-_-_-_- BOT SETUP -_-_-_-_-_-_-_-_-_-_- #


#imports from .env file
token = os.getenv('DISCORD_TOKEN')
guild = discord.Object(id=int(os.getenv('DISCORD_GUILD_ID')))

# handler and intents
handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# bot initialization
bot = commands.Bot(command_prefix='aaskwsp ', intents=intents)


# -_-_-_-_-_-_-_-_-_-_- BOT EVENTS -_-_-_-_-_-_-_-_-_-_- #


@bot.event
async def on_ready():
    print(f"Locked In: {bot.user.name}")
    try:
        synced = await bot.tree.sync(guild=guild)
        print(f"Synced {len(synced)} command(s) to the guild {guild.id}")
    
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    #if the user who sent the message is the bot itself, ignore
    if message.author == bot.user:
        return
    
    # !!! DO NOT DELETE !!!
    await bot.process_commands(message)


# -_-_-_-_-_-_-_-_-_-_- BOT COMMANDS -_-_-_-_-_-_-_-_-_-_- #


# basic hello command (mainly for testing)
@bot.tree.command(name = "hello", description = "say hello to valokwsp :3", guild=guild)
async def hello(ctx: discord.Interaction):
    await ctx.response.send_message(f"heyyy {ctx.user.mention} ;3")

# dev command
@bot.tree.command(name = "dev", description = "check out the dev ;3", guild=guild)
async def dev(ctx: discord.Interaction):
    embed = discord.Embed(title="aakwsp :3", description="i am the dev", url="https://linktr.ee/aakwsp", color=0xa872db)
    embed.set_thumbnail(url="https://media.discordapp.net/attachments/918728147472621601/1426827337571373116/basil.jpeg?ex=68eca402&is=68eb5282&hm=e31fc04ab2b1dba9c94ba4cf53cd0d2499fabf9100f91195c219163e09afc30d&=&format=webp")
    await ctx.response.send_message(embed=embed)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# add player command
@bot.tree.command(name="addaccount", description="track a valorant account", guild=guild)
@app_commands.describe(ign="in-game name", tag="in-game tag")
async def addaccount(ctx: discord.Interaction, ign: str, tag: str):
    embed = discord.Embed(title="account added", description="test", color=discord.Color.green())
    await ctx.response.send_message(embed=embed)

# remove account command 
@bot.tree.command(name="removeaccount", description="stop track a valorant account", guild=guild)
@app_commands.describe(ign="in-game name", tag="in-game tag")
async def removeaccount(ctx: discord.Interaction, ign: str, tag: str):
    embed = discord.Embed(title="account removed", description="test", color=discord.Color.red())
    await ctx.response.send_message(embed=embed)

# leaderboard command
@bot.tree.command(name="leaderboard", description="show the leaderboard of the people in this server", guild=guild)
async def leaderboard(ctx: discord.Interaction):
    embed = discord.Embed(title="leaderboard", description="test\ntest\ntest\ntest", color=discord.Color.blurple())
    await ctx.response.send_message(embed=embed)

# help command
@bot.tree.command(name="help", description="show the help menu", guild=guild)
async def help(ctx: discord.Interaction):
    await ctx.response.send_message("heelp")

# initialize command
@bot.tree.command(name="initialize", description="initialize the bot for this server", guild=guild)
async def initialize(ctx: discord.Interaction):
    embed = discord.Embed(title="initialized", description="test", color=discord.Color.green())
    await ctx.response.send_message(embed=embed)



    



bot.run(token, log_handler=handler, log_level=logging.DEBUG)