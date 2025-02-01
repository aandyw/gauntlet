import discord
from discord.ui import View, Select, Button

from tournament.base import Character


class RemoveCharacterView(View):
    def __init__(self, characters: list[Character]):
        super().__init__()
        options = [
            discord.SelectOption(
                label=f"{char.name} ({char.source})",  # Display name and source
                value=f"{char.name}|{char.source}",
            )
            for char in characters
        ]
        self.remove_select = Select(
            placeholder="Select a character to remove.",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.remove_select.callback = self.select_callback
        self.add_item(self.remove_select)

    async def select_callback(self, interaction: discord.Interaction):
        selected = self.remove_select.values[0]
        name, source = selected.split("|")
        await interaction.response.send_message(
            f"Removed character '{name}' from source '{source}'.", ephemeral=True
        )


class ListTournamentsView(View):
    pass


class VotingView(View):
    def __init__(self, characters: list[str], submit_callback):
        """
        Initializes a view with one dropdown per ranking position.

        :param characters: A list of character names to rank.
        :param submit_callback: A callback coroutine that takes (interaction, rankings)
                                where rankings is a list of character names ordered by rank.
        """
        super().__init__(timeout=300)
        self.characters = characters
        self.submit_callback = submit_callback
        self.rank_selects = {}
        total = len(characters)
        # Create a select (dropdown) for each rank position.
        for rank in range(1, total + 1):
            select = Select(
                placeholder=f"Select your choice for Rank {rank}",
                min_values=1,
                max_values=1,
                options=[
                    discord.SelectOption(label=char, value=char) for char in characters
                ],
                custom_id=f"rank_{rank}",
            )
            # Assign a simple callback to acknowledge selection changes.
            select.callback = self._make_select_callback(rank)
            self.rank_selects[rank] = select
            self.add_item(select)
        # Add a submit button to finalize the rankings.
        self.add_item(SubmitButton())

    def _make_select_callback(self, rank: int):
        async def callback(interaction: discord.Interaction):
            # For now, simply defer the response.
            await interaction.response.defer()

        return callback

    async def on_submit(self, interaction: discord.Interaction):
        # Gather selections from each dropdown.
        selections = {}
        for rank, select in self.rank_selects.items():
            if not select.values:
                await interaction.response.send_message(
                    f"Please make a selection for Rank {rank}.", ephemeral=True
                )
                return
            selections[rank] = select.values[0]
        # Ensure that all selected values are unique.
        if len(set(selections.values())) != len(self.characters):
            await interaction.response.send_message(
                "All rankings must be unique. Please reselect your choices.",
                ephemeral=True,
            )
            return
        # Build the rankings list sorted by rank.
        rankings = [selections[i] for i in sorted(selections.keys())]
        await self.submit_callback(interaction, rankings)
        self.stop()


class SubmitButton(Button):
    def __init__(self):
        super().__init__(label="Submit Rankings", style=discord.ButtonStyle.green)

    async def callback(self, interaction: discord.Interaction):
        view: VotingView = self.view  # type: ignore
        await view.on_submit(interaction)
