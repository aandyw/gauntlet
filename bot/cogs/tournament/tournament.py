import discord
from discord.ext import commands
from discord import app_commands
from itertools import combinations


class Tournament(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tournaments: dict[str, dict] = {}

    @app_commands.command(name="create", description="Create a new tournament.")
    async def create(self, interaction: discord.Interaction, name: str):
        """Create a new tournament."""
        if name in self.tournaments:
            await interaction.response.send_message(
                f"A tournament named '{name}' already exists.", ephemeral=True
            )
            return

        self.tournaments[name] = {
            "characters": [],
            "matches": [],
            "status": "open",
        }

        await interaction.response.send_message(
            f"Tournament '{name}' created successfully!"
        )

    @app_commands.command(
        name="add_character", description="Add a character to a tournament."
    )
    async def add_character(
        self, interaction: discord.Interaction, tournament_name: str, character: str
    ):
        """Add a character to a tournament."""
        tournament = self.tournaments.get(tournament_name)
        if not tournament:
            await interaction.response.send_message(
                f"Tournament '{tournament_name}' does not exist.", ephemeral=True
            )
            return

        if tournament["status"] != "open":
            await interaction.response.send_message(
                "Cannot add characters to a tournament that is not open.",
                ephemeral=True,
            )
            return

        if character in tournament["characters"]:
            await interaction.response.send_message(
                f"Character '{character}' is already in the tournament.", ephemeral=True
            )
            return

        tournament["characters"].append(character)
        await interaction.response.send_message(
            f"Character '{character}' added to tournament '{tournament_name}'."
        )

    @app_commands.command(name="list", description="List all tournaments.")
    async def list_tournaments(self, interaction: discord.Interaction):
        """List all tournaments."""
        if not self.tournaments:
            await interaction.response.send_message(
                "No tournaments have been created yet.", ephemeral=True
            )
            return

        embed = discord.Embed(title="Tournaments", color=discord.Color.blue())
        for name, details in self.tournaments.items():
            embed.add_field(
                name=name,
                value=f"Status: {details['status']}\nCharacters: {len(details['characters'])}",
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="start", description="Start a tournament.")
    async def start_tournament(self, interaction: discord.Interaction, name: str):
        """Start a tournament."""
        tournament = self.tournaments.get(name)
        if not tournament:
            await interaction.response.send_message(
                f"Tournament '{name}' does not exist.", ephemeral=True
            )
            return

        if tournament["status"] != "open":
            await interaction.response.send_message(
                f"Tournament '{name}' is already started or completed.", ephemeral=True
            )
            return

        if len(tournament["characters"]) < 2:
            await interaction.response.send_message(
                f"Tournament '{name}' needs at least two characters to start.",
                ephemeral=True,
            )
            return

        tournament["matches"] = list(combinations(tournament["characters"], 2))
        tournament["status"] = "ongoing"
        await interaction.response.send_message(
            f"Tournament '{name}' started with {len(tournament['matches'])} matches!"
        )

    @app_commands.command(name="view", description="View tournament details.")
    async def view_tournament(self, interaction: discord.Interaction, name: str):
        """View tournament details."""
        tournament = self.tournaments.get(name)
        if not tournament:
            await interaction.response.send_message(
                f"Tournament '{name}' does not exist.", ephemeral=True
            )
            return

        embed = discord.Embed(title=f"Tournament: {name}", color=discord.Color.green())
        embed.add_field(name="Status", value=tournament["status"], inline=False)
        embed.add_field(
            name="Characters",
            value=", ".join(tournament["characters"]) or "None",
            inline=False,
        )
        embed.add_field(name="Matches", value=len(tournament["matches"]), inline=False)
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Tournament(bot))
