import discord
from tournament.base import Character, Tournament
from utils import logger
import traceback


class AddCharacterModal(discord.ui.Modal, title="Add New Character"):
    char_name = discord.ui.TextInput(
        label="Character Name",
        placeholder="Enter the name of the character.",
        required=True,
        max_length=50,
    )

    char_source = discord.ui.TextInput(
        label="Character Source",
        placeholder="Where is this character from?",
        required=True,
        max_length=100,
    )

    def __init__(self, tournament: Tournament, tournament_cog):
        super().__init__()
        self.tournament = tournament
        self.tournament_cog = tournament_cog

    async def on_submit(self, interaction: discord.Interaction):
        char_name = self.char_name.value.strip()
        char_source = self.char_source.value.strip()

        for existing_char in self.tournament.characters:
            if (
                existing_char.name.lower() == char_name.lower()
                and char_source.lower() == existing_char.source.lower()
            ):
                await interaction.response.send_message(
                    f"Character '{char_name}' from '{char_source}' is already in the tournament.",
                    ephemeral=True,
                )
                return

        new_character = Character(name=char_name, source=char_source)
        self.tournament.characters.append(new_character)

        # TODO: Save to the database
        # await self.tournament_cog.save_tournament_to_db(tournament)

        await interaction.response.send_message(
            f"Character '{char_name}' added to tournament '{self.tournament.name}'.",
            ephemeral=True,
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )
        logger.error(traceback.print_exception(type(error), error, error.__traceback__))
