from itertools import combinations

import discord
from discord import app_commands
from discord.ext import commands
from tournament.base import Match, Tournament, TournamentStatus, User, Voter
from tournament.modals import AddCharacterModal
from tournament.views import RemoveCharacterView


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
                f"Tournament '{name}' already exists.", ephemeral=True
            )
            return

        user = User(id=interaction.user.id, name=interaction.user.name)
        self.tournaments[name] = Tournament(name=name, creator=user)
        await interaction.response.send_message(
            f"Tournament '{name}' created successfully!", ephemeral=True
        )

    @app_commands.command(name="delete", description="Delete a tournament.")
    async def delete(self, interaction: discord.Interaction, name: str):
        if name not in self.tournaments:
            await interaction.response.send_message(
                f"Tournament '{name}' does not exist.", ephemeral=True
            )
            return

        creator_id = self.tournaments[name].creator.id

        if creator_id == interaction.user.id:
            del self.tournaments[name]

            await interaction.response.send_message(
                f"Tournament '{name}' removed successfully!", ephemeral=True
            )
        else:
            await interaction.response.send_message(
                "Only the creator of the tournament can delete it.", ephemeral=True
            )

    @app_commands.command(name="start", description="Start a tournament.")
    async def start(self, interaction: discord.Interaction, name: str):
        tournament = await self._get_tournament(interaction, name)

        if tournament:
            if tournament.status != TournamentStatus.OPEN:
                await interaction.response.send_message(
                    f"Tournament '{name}' is already started or completed.",
                    ephemeral=True,
                )
                return

            # Set number of characters required to start here
            if len(tournament.characters) < 2:
                await interaction.response.send_message(
                    f"Tournament '{name}' needs at least two characters to start.",
                    ephemeral=True,
                )
                return

            # TODO: Modification here with how we are managing matches
            possible_combinations = list(combinations(tournament.characters, 2))

            # Create matches
            for a, b in possible_combinations:
                tournament.matches.append(Match(a=a, b=b))

            tournament.status = TournamentStatus.ONGOING
            await interaction.response.send_message(f"Tournament '{name}' ongoing!")

    @app_commands.command(name="end", description="End a tournament.")
    async def end(self, interaction: discord.Interaction, name: str):
        tournament = await self._get_tournament(interaction, name)

        if tournament:
            if tournament.status != TournamentStatus.ONGOING:
                await interaction.response.send_message(
                    f"Cannot end Tournament '{name}'. Tournament is not ongoing.",
                    ephemeral=True,
                )
                return

            tournament.status = TournamentStatus.COMPLETED
            await interaction.response.send_message(f"Tournament '{name}' completed!")

    @app_commands.command(
        name="view",
        description="View details of a tournament.",
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
                value=", ".join(char.name for char in tournament.characters) or "",
                inline=False,
            )
            embed.add_field(
                name="Voters",
                value=", ".join(
                    voter.name for voter in tournament.registered_voters.values()
                )
                or "",
                inline=False,
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)

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
                    f"Status: {tournament.status}\n"
                    f"Characters: {len(tournament.characters)}\n"
                    f"Creator: {tournament.creator.name}"
                ),
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

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

    ### Characters ###
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
        self, interaction: discord.Interaction, tourney_name: str
    ):
        tournament = await self._get_tournament(interaction, tourney_name)

        if tournament:
            if tournament.status != TournamentStatus.OPEN:
                await interaction.response.send_message(
                    "Cannot remove characters from a tournament that is not open.",
                    ephemeral=True,
                )
                return

            # TODO: Fix error when no characters are present to remove
            if len(self.tournaments[tourney_name].characters) == 0:
                await interaction.response.send_message(
                    "No characters to remove.", ephemeral=True
                )
                return

            await interaction.response.send_message(
                view=RemoveCharacterView(self.tournaments[tourney_name].characters),
                ephemeral=True,
            )

    ### Voters ###
    @app_commands.command(
        name="register", description="Register as a voter for a tournament."
    )
    async def register(self, interaction: discord.Interaction, tourney_name: str):
        tournament = await self._get_tournament(interaction, tourney_name)

        if tournament:
            user_id = interaction.user.id
            if user_id in tournament.registered_voters:
                await interaction.response.send_message(
                    "You are already registered as a voter for this tournament.",
                    ephemeral=True,
                )
                return

            voter = Voter(id=user_id, name=interaction.user.name)
            tournament.registered_voters[user_id] = voter
            await interaction.response.send_message(
                "You have been registered as a voter for this tournament.",
                ephemeral=True,
            )

    @app_commands.command(
        name="unregister", description="Unregister as a voter for a tournament."
    )
    async def unregister(self, interaction: discord.Interaction, tourney_name: str):
        tournament = await self._get_tournament(interaction, tourney_name)

        if tournament:
            user_id = interaction.user.id
            if user_id not in tournament.registered_voters:
                await interaction.response.send_message(
                    "You are not registered as a voter for this tournament.",
                    ephemeral=True,
                )
                return

            del tournament.registered_voters[user_id]
            await interaction.response.send_message(
                "You have been unregistered as a voter for this tournament.",
                ephemeral=True,
            )


async def setup(bot):
    await bot.add_cog(TournamentCog(bot))
