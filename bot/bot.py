from os import getenv

import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import logger

load_dotenv()


class GuantletBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        super().__init__(command_prefix="$", intents=intents)

    # Load the tournament cog
    async def _load_extensions(self):
        extensions = ["cogs.guantlet.tournament", "cogs.yap"]
        for extension in extensions:
            await self.load_extension(extension)

    # Run whenever bot starts
    async def setup_hook(self):
        await self._load_extensions()

    async def on_ready(self):
        logger.info(f"Bot is online as {self.user}")
        try:
            synced = await self.tree.sync()  # Sync all slash commands
            logger.info(f"Synced {len(synced)} commands.")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")


if __name__ == "__main__":
    TOKEN = getenv("DISCORD_TOKEN")

    if not TOKEN:
        raise ValueError("Discord token is not set or invalid.")

    GuantletBot().run(TOKEN)
