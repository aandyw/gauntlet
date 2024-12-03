import discord
from discord.ext import commands

from dotenv import load_dotenv
from os import getenv

from bot.cogs.tournament.tournament import TournamentView

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="", intents=intents, application_id=getenv("APPLICATION_ID")
)


@bot.event
async def on_ready():
    print(f"Bot is online as {bot.user}")
    try:
        synced = await bot.tree.sync()  # Sync all slash commands
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


# @bot.tree.command(name="create", description="Create a new tournament")
# async def create(interaction: discord.Interaction):
#     try:
#         await interaction.user.send("Hello! Creating tourney!")
#         await interaction.response.send_message("Check your DMs! 📩", ephemeral=True)
#     except discord.Forbidden:
#         await interaction.response.send_message(
#             "I couldn't send you a DM. Please check your DM privacy settings.",
#             ephemeral=True,
#         )


@bot.tree.command(name="create")
async def create(interaction: discord.Interaction):
    view = TournamentView()
    await interaction.response.send_message(
        "Click the button below to create a tournament!", view=view, ephemeral=True
    )


@bot.tree.command(name="register", description="Register for a tourney")
async def register(interaction: discord.Interaction):
    try:
        await interaction.user.send("Hello! Registering for tourney!")
        await interaction.response.send_message("Check your DMs! 📩", ephemeral=True)
    except discord.Forbidden:
        await interaction.response.send_message(
            "I couldn't send you a DM. Please check your DM privacy settings.",
            ephemeral=True,
        )


discord_token = getenv("DISCORD_TOKEN")

if not discord_token:
    raise ValueError("Discord token is not set or invalid.")

bot.run(discord_token)
