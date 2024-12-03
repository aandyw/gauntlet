import discord

from .modals import Tournament


class TournamentModal(discord.ui.Modal, title="Create Tournament"):
    name = discord.ui.TextInput(
        label="Tournament Name",
        style=discord.TextStyle.short,
        placeholder="Enter tournament name",
        max_length=100,
    )

    async def on_submit(self, interaction: discord.Interaction):
        tournament_name = self.name.value
        tournament = Tournament(name=tournament_name, creator=interaction.user)

        try:
            await interaction.user.send(
                f"Your tournament '{tournament_name}' has been created! 🎉"
            )
            await interaction.response.send_message(
                f"Tournament '{tournament_name}' created successfully! Check your DMs.",
                ephemeral=True,
            )
            print(f"New Tournament Created: {tournament}")
        except discord.Forbidden:
            await interaction.response.send_message(
                "I couldn't send you a DM. Please check your DM privacy settings.",
                ephemeral=True,
            )
