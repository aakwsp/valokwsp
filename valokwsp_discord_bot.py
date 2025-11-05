# -*- coding: utf-8 -*-

import discord
from discord import app_commands
from discord.ext import commands
import logging
import os
import get_info
from typing import Tuple 


# -_-_-_-_-_-_-_-_-_-_- BOT SETUP -_-_-_-_-_-_-_-_-_-_- #
# load .env variables
get_info.load_env()

#imports from .env file 
token = os.getenv('DISCORD_TOKEN') #str
guild = discord.Object(id=int(os.getenv('DISCORD_GUILD_ID'))) #discord.Object
api_key = os.environ.get("RIOT_API_KEY") #str
base = os.environ.get("RIOT_API_BASE") #str

# handler and intents
handler = logging.FileHandler(filename='zzz_discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

# bot initialization
bot = commands.Bot(command_prefix='aaskwsp ', intents=intents)

DEBUG = True

# -_-_-_-_-_-_-_-_-_-_- HELPER FUNCTIONS -_-_-_-_-_-_-_-_-_-_- #

def decode_riot_api_error(status: dict) -> Tuple[str, str]:
    '''
    decodes the error from the API response.
    helper function for parse_riot_api_error

    returns:
    Tuple[str, str]: (error_code, error_message)
    '''
    custom_error_messages = {
        400: "Bad request. Check your input format.",
        401: "Unauthorized. Your API key is invalid or expired.",
        403: "Forbidden. You don't have permission or your API key is restricted.",
        404: "Account not found. Check IGN, tag, and region.",
        408: "Request timed out. Riot servers may be slow.",
        429: "Rate limit hit. Slow down your requests.",
        500: "Riot server error. Try again later.",
        502: "Bad gateway. Riot servers are having issues.",
        503: "Service unavailable. Riot is down.",
        504: "Gateway timeout. Riot server took too long."
    }
    
    code = status.get('status_code')

    # error has error code, (replace with custom message)
    if code in custom_error_messages:
        return code, custom_error_messages[code]

    # most likely a new error code not in the dictionary
    return code, "error code not in dictionary"

def parse_riot_api_error(raw) -> Tuple[str, str] | None:
    '''Checks if the API response contains an error. 
    
    returns:
    Tuple[str, str]: (error_code, error_message) if error exists
    None: if no error
    '''

    # raw is missing or wrong type
    if not isinstance(raw, dict):
        return "UNKNOWN", "api returned invalid response"

    status = raw.get("status")

    # not an error if it doesnt have status
    if not isinstance(status, dict):
        return None
    
    code = status.get("status_code")

    # error has error code, (custom error codes)
    return decode_riot_api_error(status)



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

@bot.tree.command(name="findaccount", description="get puuid", guild=guild)
@app_commands.describe(name="ign", tag="tag", region="region")
@app_commands.choices(region=[
    app_commands.Choice(name="Americas", value="americas"),
    app_commands.Choice(name="Europe", value="europe"),
    app_commands.Choice(name="Asia", value="asia"),
])
async def findaccount(ctx: discord.Interaction, name: str, tag: str, region: str):
    endpoint = "riot/account/v1/accounts/by-riot-id"
    if DEBUG: print(f"NAME:{name}, TAG:{tag}, REGION:{region}\n")
    raw = get_info.from_endpoint(region, name, tag, base, endpoint, api_key)
    error = parse_riot_api_error(raw)

    # if it has error, send error message and return
    if error != None:
        error_code, error_message = error
        if DEBUG: print(f"error found: {error_code}: {error_message}\n")
        embed = discord.Embed(
            title="an error has occurred", 
            description=f"error code: {error_code}\nmessage: {error_message}", 
            color=discord.Color.red()
        )

    else: 
        puuid = raw['puuid']
        gameName = raw['gameName']
        tagLine = raw['tagLine']
        if DEBUG: print(f"account found: {gameName}#{tagLine}\npuuid: {puuid}\n")
        embed = discord.Embed(
            title="account found", 
            description=f"riot id {gameName}#{tagLine} \npuuid: {puuid}", 
            color=discord.Color.green()
        )
    
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