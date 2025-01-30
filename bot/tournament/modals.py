import discord
from tournament.base import Character, Tournament


class AddCharacterModal(discord.ui.Modal, title="Add New Character"):
    char_name = discord.ui.TextInput(
        label="Character Name",
        placeholder="Enter the character's name...",
        required=True,
        max_length=50,
    )

    def __init__(self, tournament: Tournament, tournament_cog):
        super().__init__()
        self.tournament = tournament
        self.tournament_cog = tournament_cog

    async def on_submit(self, interaction: discord.Interaction):
        char_name = self.char_name.value.strip()

        if any(
            existing_char.name.lower() == char_name.lower()
            for existing_char in self.tournament.characters
        ):
            await interaction.response.send_message(
                f"Character '{char_name}' is already in the tournament.",
                ephemeral=True,
            )
            return

        new_character = Character(name=char_name)
        self.tournament.characters.append(new_character)

        # TODO: Save to the database
        # await self.tournament_cog.save_tournament_to_db(tournament)

        await interaction.response.send_message(
            f"Character '{char_name}' added to tournament '{self.tournament.name}'.",
            ephemeral=True,
        )


class Feedback(discord.ui.Modal, title="Feedback"):
    # Our modal classes MUST subclass `discord.ui.Modal`,
    # but the title can be whatever you want.

    # This will be a short input, where the user can enter their name
    # It will also have a placeholder, as denoted by the `placeholder` kwarg.
    # By default, it is required and is a short-style input which is exactly
    # what we want.
    name = discord.ui.TextInput(
        label="Name",
        placeholder="Your name here...",
    )

    # This is a longer, paragraph style input, where user can submit feedback
    # Unlike the name, it is not required. If filled out, however, it will
    # only accept a maximum of 300 characters, as denoted by the
    # `max_length=300` kwarg.
    feedback = discord.ui.TextInput(
        label="What do you think of this new feature?",
        style=discord.TextStyle.long,
        placeholder="Type your feedback here...",
        required=False,
        max_length=300,
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message(
            f"Thanks for your feedback, {self.name.value}!", ephemeral=True
        )

    async def on_error(
        self, interaction: discord.Interaction, error: Exception
    ) -> None:
        await interaction.response.send_message(
            "Oops! Something went wrong.", ephemeral=True
        )

        # Make sure we know what the error actually is
        # traceback.print_exception(type(error), error, error.__traceback__)
