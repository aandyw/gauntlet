import discord
import asyncio
from discord.ext.commands import Cog
from discord import Interaction, Role, TextChannel
from discord.app_commands import Choice, command, autocomplete

from utils import logger, DiscordMessageError

from dataclasses import dataclass


@dataclass
class YapSession:
    role: Role
    minutes: int
    task: asyncio.Task


active_yaps: dict[int, YapSession] = {}


class YapCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    def _fetch_role(self, interaction: Interaction, role_name: str) -> Role:
        """
        Fetch the role object from the guild.
        """

        if not interaction.guild:
            raise DiscordMessageError("This command must be used in a server.")

        # Fetch role object
        role = discord.utils.get(interaction.guild.roles, id=int(role_name))

        if not role:
            raise DiscordMessageError("Invalid role selection.")

        return role

    async def _role_autocomplete(
        self, interaction: Interaction, current: str
    ) -> list[Choice[str]]:
        if not interaction.guild:
            return []

        roles = [role for role in interaction.guild.roles if role.name != "@everyone"]

        return [
            Choice(name=role.name, value=str(role.id))
            for role in roles
            if current.lower() in role.name.lower()
        ][:25]

    async def _yap_ping(self, channel: TextChannel, role: Role, minutes: int) -> None:
        """
        Yapping. Sends the ping to the role and channel every X minutes.
        """

        while True:
            logger.info("I'm about to yap...")
            await asyncio.sleep(minutes * 60)
            await channel.send(f"{role.mention} hop on if you")

    @command(
        name="yap",
        description="Create a yap session (reminder) in this channel that yaps every X minutes.",
    )
    @autocomplete(role_name=_role_autocomplete)
    async def yap(self, interaction: Interaction, role_name: str, minutes: int) -> None:
        try:
            role = self._fetch_role(interaction, role_name)

            channel = interaction.channel
            if not channel or not isinstance(channel, TextChannel):
                await interaction.response.send_message(
                    "Could not find a valid channel.", ephemeral=True
                )
                return

            # Check if yap session already exists
            if role.id in active_yaps:
                await interaction.response.send_message(
                    f"A yap session for {role.mention} is already running!",
                    ephemeral=True,
                )
                return

            # Start the reminder task
            task = asyncio.create_task(self._yap_ping(channel, role, minutes))
            active_yaps[role.id] = YapSession(role=role, minutes=minutes, task=task)

            logger.info(
                f"Created yapping session for {role.name} ({role.id}) every {minutes} minutes."
            )

            await interaction.response.send_message(
                f"{interaction.user.mention} created a yap session for {role.mention} "
                f"for every {minutes} minutes."
            )
        except DiscordMessageError as e:
            await interaction.response.send_message(e, ephemeral=True)
            return

    @command(
        name="mog",
        description="Silence / delete an existing yap session.",
    )
    @autocomplete(role_name=_role_autocomplete)
    async def mog(self, interaction: Interaction, role_name: str) -> None:
        try:
            role = self._fetch_role(interaction, role_name)

            if role.id not in active_yaps:
                await interaction.response.send_message(
                    f"No yap session found for {role.mention}.", ephemeral=True
                )
                return

            yap_session = active_yaps[role.id]
            yap_session.task.cancel()
            del active_yaps[role.id]

            logger.info(f"Deleted yapping session for {role.name} ({role.id}).")

            await interaction.response.send_message(
                f"{interaction.user.mention} mog'd the yap session for {role.mention}."
            )
        except DiscordMessageError as e:
            await interaction.response.send_message(e, ephemeral=True)
            return

    @command(
        name="view-yaps",
        description="View all active yap sessions.",
    )
    async def view_yaps(self, interaction: Interaction) -> None:
        if not active_yaps:
            await interaction.response.send_message("No active yap sessions.")
            return

        embed = discord.Embed(title="Active Yaps:", color=discord.Color.green())
        for yap_session in active_yaps.values():
            embed.add_field(
                name="",
                value=f"{yap_session.role.mention} Yapping every {yap_session.minutes} minutes.",
                inline=False,
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)


async def setup(bot):
    await bot.add_cog(YapCog(bot))
