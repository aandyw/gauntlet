from itertools import combinations

import discord
from tournament.base import Character, Tournament, TournamentStatus, Match
from tournament.modals import AddCharacterModal
from discord import app_commands
from discord.ext import commands


class TournamentCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tournaments: dict[str, Tournament] = {}

    async def _get_tournament(
        self, interaction: discord.Interaction, name: str
    ) -> Tournament | None:
        tournament = self.tournaments.get(name)

        if not tournament:
            await interaction.response.send_message(
                f"Tournament '{name}' does not exist.", ephemeral=True
            )
            return

        return tournament

    @app_commands.command(name="create", description="Create a new tournament.")
    async def create(self, interaction: discord.Interaction, name: str):
        if name in self.tournaments:
            await interaction.response.send_message(
                f"A tournament named '{name}' already exists.", ephemeral=True
            )
            return

        self.tournaments[name] = Tournament(name=name)
        await interaction.response.send_message(
            f"Tournament '{name}' created successfully!"
        )

    @app_commands.command(name="list", description="List all tournaments.")
    async def list(self, interaction: discord.Interaction):
        if not self.tournaments:
            await interaction.response.send_message(
                "No tournaments have been created yet.", ephemeral=True
            )
            return

        # TODO: Turn these into views / modals
        embed = discord.Embed(title="Tournaments", color=discord.Color.blue())
        for name, tournament in self.tournaments.items():
            embed.add_field(
                name=name,
                value=(
                    f"Status: {tournament.status}"
                    f"Characters: {len(tournament.characters)}"
                ),
                inline=False,
            )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="start", description="Start a tournament.")
    async def start(self, interaction: discord.Interaction, name: str):
        tournament = await self._get_tournament(interaction, name)

        if tournament:
            if tournament.status != "open":
                await interaction.response.send_message(
                    f"Tournament '{name}' is already started or completed.",
                    ephemeral=True,
                )
                return

            if len(tournament.characters) < 2:
                await interaction.response.send_message(
                    f"Tournament '{name}' needs at least two characters to start.",
                    ephemeral=True,
                )
                return

            possible_combinations = list(combinations(tournament.characters, 2))

            # Create matches
            for a, b in possible_combinations:
                tournament.matches.append(Match(a=a, b=b))

            tournament.status = TournamentStatus.ONGOING
            await interaction.response.send_message(
                f"Tournament '{name}' started with {len(tournament.matches)} matches!"
            )

    @app_commands.command(
        name="view",
        description="View tournament details about who is registered and other details",
    )
    async def view(self, interaction: discord.Interaction, name: str):
        tournament = await self._get_tournament(interaction, name)

        # TODO: show registered users
        if tournament:
            embed = discord.Embed(
                title=f"Tournament: {name}", color=discord.Color.green()
            )
            embed.add_field(name="Status", value=tournament.status, inline=False)
            embed.add_field(
                name="Characters",
                value=", ".join(char.name for char in tournament.characters) or "None",
                inline=False,
            )
            embed.add_field(name="Matches", value=len(tournament.matches), inline=False)
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="add", description="Add a character to a tournament.")
    async def add_character(self, interaction: discord.Interaction, tourney_name: str):
        tournament = await self._get_tournament(interaction, tourney_name)

        if tournament:
            if tournament.status != TournamentStatus.OPEN:
                await interaction.response.send_message(
                    "Cannot add characters to a tournament that is not open.",
                    ephemeral=True,
                )
                return

            # Send add character modal to tournament master
            modal = AddCharacterModal(tournament, self)
            await interaction.response.send_modal(modal)

    @app_commands.command(
        name="remove", description="Remove a character from a tournament."
    )
    async def remove_character(
        self, interaction: discord.Interaction, tourney_name: str, char_name: str
    ):
        tournament = await self._get_tournament(interaction, tourney_name)

        if tournament:
            if tournament.status != TournamentStatus.OPEN:
                await interaction.response.send_message(
                    "Cannot remove characters from a tournament that is not open.",
                    ephemeral=True,
                )
                return

            for idx, char in enumerate(tournament.characters):
                if char.name == char_name:
                    del tournament.characters[idx]
                    await interaction.response.send_message(
                        f"Character '{char_name}' removed from tournament '{tourney_name}'."
                    )
                    return

            await interaction.response.send_message(
                f"Character '{char_name}' not found in tournament '{tourney_name}'.",
                ephemeral=True,
            )

    @app_commands.command(
        name="leaderboard", description="Display the leaderboard of a tournament"
    )
    async def leaderboard(self, interaction: discord.Interaction, tourney_name: str):
        tournament = await self._get_tournament(interaction, tourney_name)

        if tournament:
            # Get the sorted leaderboard
            leaderboard = tournament.create_leaderboard()

            # Create the embed
            embed = discord.Embed(
                title=f"Leaderboard for Tournament '{tourney_name}'",
                color=discord.Color.gold(),
            )
            for idx, character in enumerate(leaderboard, start=1):
                embed.add_field(
                    name=f"{idx}. {character.name}",
                    value=f"ELO: {character.elo}",
                    inline=False,
                )

            await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(TournamentCog(bot))
