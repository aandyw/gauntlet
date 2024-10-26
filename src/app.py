import discord
from discord.ext import commands

from dotenv import load_dotenv
from os import getenv

load_dotenv()

# Create a bot instance with a command prefix (e.g., "!")
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


@bot.command()
async def create(ctx):
    await ctx.send("creating tourney!")


discord_token = getenv("DISCORD_TOKEN")

if not discord_token:
    raise ValueError("Discord token is not set or invalid.")

bot.run(discord_token)
