import discord
from discord.ui import View, Button
from .models import Tournament


class TournamentView(View):
    def __init__(self, tournament: Tournament):
        super().__init__()
        self.tournament = tournament

    @discord.ui.button(label="Add Candidate", style=discord.ButtonStyle.primary)
    async def add_candidate(self, button: Button, interaction: discord.Interaction):
        await interaction.response.send_message(
            "Use `/add_candidate` to add a candidate."
        )
