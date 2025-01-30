from enum import StrEnum, auto
from uuid import uuid4

from pydantic import BaseModel, Field


class Character(BaseModel):
    name: str = Field(..., examples=["Anya"])
    elo: float = 1000.0

    def __str__(self) -> str:
        return self.name


class Match(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex)
    a: Character = Field(...)
    b: Character = Field(...)
    votes: int = 0
    winner: Character | None = None


class TournamentStatus(StrEnum):
    OPEN = auto()
    ONGOING = auto()
    COMPLETED = auto()


class Voter(BaseModel):
    name: str = Field(...)  # discord id?
    voted: bool = False


class Tournament(BaseModel):
    name: str = Field(...)
    status: TournamentStatus = TournamentStatus.OPEN
    characters: list[Character] = []
    matches: list[Match] = []
    registered_voters: list[Voter] = []

    # TODO: add closing time

    def __str__(self):
        return self.name

    def __repr__(self):
        return f"<Tournament name={self.name!r} status={self.status!r}>"

    def create_leaderboard(self, top_k: int = -1) -> list[Character]:
        """Create a leaderboard of the top k characters.

        Args:
            top_k (int, optional): Number of top characters to return.
                If none specified, return all characters. Defaults to -1.

        Returns:
            list[Character]: The leaderboard of characters.
        """

        return sorted(self.characters, key=lambda c: c.elo, reverse=True)[:top_k]
